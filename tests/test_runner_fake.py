"""End-to-end tests for the Readback loop against FakeAdapters. No network."""

from __future__ import annotations

import pytest

from readback.adapters.fake import FakeAdapter
from readback.core import wal as wal_mod
from readback.core.receipt import (
    OUTCOME_FAILURE,
    OUTCOME_HELD,
    OUTCOME_PARTIAL,
    OUTCOME_SUCCESS,
)
from readback.core.runner import run
from readback.core.wal import WAL
from readback.planner import plan_request
from readback.types import IrreversibleEffect

REFUND_REQUEST = "Refund order 4417 and log the reason."
UNBOUNDED_REQUEST = "Refund everything from last week."


@pytest.fixture
def adapters() -> dict[str, FakeAdapter]:
    return {name: FakeAdapter(name=name) for name in ("stripe", "notion", "slack")}


@pytest.fixture
def root(tmp_path) -> str:
    """Isolate WALs and receipts per test."""
    return str(tmp_path / "runs")


def test_happy_path_all_verifications_pass(adapters, root):
    """Three effects apply, all three read-back assertions pass, outcome success."""
    receipt = run(REFUND_REQUEST, adapters=adapters, root=root)

    assert receipt.outcome == OUTCOME_SUCCESS, receipt.reason
    assert len(receipt.planned) == 3
    assert {e["app"] for e in receipt.planned} == {"stripe", "notion", "slack"}

    applied = [c for c in receipt.calls if c.phase == "apply"]
    assert len(applied) == 3
    assert all(c.status == "ok" for c in applied)

    assert len(receipt.verifications) == 3
    assert all(v.passed for v in receipt.verifications)

    # Nothing was rolled back.
    assert not [c for c in receipt.calls if c.phase == "compensate"]

    # Every effect is present in live state, exactly once.
    for adapter in adapters.values():
        assert len(adapter.store) == 1
        assert all(count == 1 for count in adapter.write_count.values())

    # The WAL agrees.
    records = WAL.replay(receipt.run_id, root=root)
    committed = [r for r in records if r["state"] == wal_mod.COMMITTED]
    assert len(committed) == 3


def test_verify_failure_compensates_every_reversible_effect(adapters, root):
    """One verify fails -> every REVERSIBLE effect is undone; the refund is not.

    This scenario refunds, so it cannot end in a clean rollback: a committed
    refund has no inverse. The honest outcome is PARTIAL_MANUAL_REMEDIATION
    naming the Stripe object, with Slack and Notion fully reversed.

    This test used to assert a clean `failure` with all three stores emptied.
    That only passed because FakeAdapter ignored `Effect.reversible` and
    deleted the refund record -- the fake was reversing something production
    refuses to reverse. See tests/test_adapter_contract.py.
    """
    # Let the Notion write land, then drift live state out from under it. This is
    # the silent-divergence case read-back exists to catch.
    notion = adapters["notion"]
    original_apply = notion.apply

    def apply_then_drift(effect):
        result = original_apply(effect)
        notion.drift(effect.idempotency_key, reason="SOMETHING ELSE ENTIRELY")
        return result

    notion.apply = apply_then_drift

    receipt = run(REFUND_REQUEST, adapters=adapters, root=root)

    assert receipt.outcome == OUTCOME_PARTIAL
    assert receipt.outcome != OUTCOME_SUCCESS
    assert "notion.append_audit_row" in receipt.reason
    assert "SOMETHING ELSE ENTIRELY" in receipt.reason

    failed = [v for v in receipt.verifications if not v.passed]
    assert len(failed) == 1
    assert failed[0].app == "notion"

    # Rollback is attempted in reverse commit order. Commit order is notion,
    # slack, stripe because the runner sorts the irreversible refund last, so
    # rollback runs stripe, slack, notion -- and stripe refuses.
    compensations = [c for c in receipt.calls if c.phase == "compensate"]
    assert [c.app for c in compensations] == ["stripe", "slack", "notion"]
    assert compensations[0].status == "irreversible"
    assert all(c.status in ("ok", "skipped") for c in compensations[1:])

    # Everything reversible is gone; the refund remains and is reported.
    assert adapters["slack"].store == {}
    assert adapters["notion"].store == {}
    assert list(adapters["stripe"].store) == ["stripe:refund:order-4417"]

    assert len(receipt.manual_remediation) == 1
    assert receipt.manual_remediation[0].app == "stripe"
    assert "4417" in receipt.manual_remediation[0].object_id

    records = WAL.replay(receipt.run_id, root=root)
    compensated = [r for r in records if r["state"] == wal_mod.COMPENSATED]
    assert len(compensated) == 2, "the irreversible refund is never marked COMPENSATED"


def test_crash_mid_run_then_retry_does_not_double_write(adapters, root):
    """Crash after the first write, replay the WAL, retry: no effect applies twice."""
    notion = adapters["notion"]
    slack = adapters["slack"]

    class Boom(RuntimeError):
        pass

    # Effects run notion, slack, stripe: the irreversible refund is sorted last.
    # Crash on the SECOND effect so exactly one write has committed first.
    def crash(effect):
        raise Boom("process died mid-run")

    slack.apply = crash

    run_id = "run_crash_test"
    with pytest.raises(Boom):
        run(REFUND_REQUEST, adapters=adapters, run_id=run_id, root=root)

    # The Notion audit row committed before the crash.
    assert len(notion.store) == 1
    records = WAL.replay(run_id, root=root)
    assert [r["state"] for r in records] == [
        wal_mod.INTENDED, wal_mod.COMMITTED, wal_mod.INTENDED
    ]

    # Retry the SAME run id. The WAL is replayed and the Notion write is skipped.
    del slack.apply  # restore the real method
    receipt = run(REFUND_REQUEST, adapters=adapters, run_id=run_id, root=root)

    assert receipt.outcome == OUTCOME_SUCCESS, receipt.reason

    notion_applies = [c for c in receipt.calls if c.app == "notion" and c.phase == "apply"]
    assert len(notion_applies) == 1
    assert notion_applies[0].status == "skipped", "retry must not re-apply a committed effect"

    # The idempotency key proves it: written exactly once across both attempts.
    key = "notion:audit:refund-order-4417"
    assert notion.write_count[key] == 1
    assert all(count == 1 for a in adapters.values() for count in a.write_count.values())


def test_risk_gate_holds_unbounded_request_with_zero_effects(adapters, root):
    """An unbounded request is held before any provider is touched."""
    receipt = run(UNBOUNDED_REQUEST, adapters=adapters, root=root)

    assert receipt.outcome == OUTCOME_HELD
    assert receipt.gate["verdict"] == "hold"
    assert "unbounded scope" in receipt.reason.lower()

    # Zero effects applied, zero verifications, zero live state, empty WAL.
    assert receipt.calls == []
    assert receipt.verifications == []
    assert all(adapter.store == {} for adapter in adapters.values())
    assert WAL.replay(receipt.run_id, root=root) == []

    # And the planner never produced effects for it either.
    assert plan_request(UNBOUNDED_REQUEST).effects == []


def test_irreversible_committed_effect_yields_partial_not_success(adapters, root):
    """A committed effect with no inverse must never be reported as a clean rollback.

    The refund is the irreversible one, so this makes its compensation raise
    the way the real Stripe adapter does, then fails read-back on Notion. The
    run must reverse everything else, name the Stripe object, and land on
    PARTIAL_MANUAL_REMEDIATION -- not success, and not plain failure.
    """
    stripe = adapters["stripe"]
    notion = adapters["notion"]

    def refuse_to_compensate(effect):
        raise IrreversibleEffect(
            "a refund cannot be un-refunded",
            app="stripe",
            object_id="pi_TEST_IRREVERSIBLE",
        )

    stripe.compensate = refuse_to_compensate

    original_apply = notion.apply

    def apply_then_drift(effect):
        result = original_apply(effect)
        notion.drift(effect.idempotency_key, reason="DRIFTED")
        return result

    notion.apply = apply_then_drift

    receipt = run(REFUND_REQUEST, adapters=adapters, root=root)

    assert receipt.outcome == OUTCOME_PARTIAL
    assert receipt.outcome != OUTCOME_SUCCESS

    # The un-reversible effect is named, with the object a human needs.
    assert len(receipt.manual_remediation) == 1
    item = receipt.manual_remediation[0]
    assert item.app == "stripe"
    assert item.object_id == "pi_TEST_IRREVERSIBLE"
    assert "pi_TEST_IRREVERSIBLE" in receipt.reason

    # Everything that COULD be reversed still was.
    compensated = [c for c in receipt.calls if c.phase == "compensate"]
    assert {c.app for c in compensated if c.status in ("ok", "skipped")} == {"slack", "notion"}
    assert adapters["slack"].store == {}
    assert notion.store == {}
