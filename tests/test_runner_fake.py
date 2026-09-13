"""End-to-end tests for the Readback loop against FakeAdapters. No network."""

from __future__ import annotations

import pytest

from readback.adapters.fake import FakeAdapter
from readback.core import wal as wal_mod
from readback.core.receipt import OUTCOME_FAILURE, OUTCOME_HELD, OUTCOME_SUCCESS
from readback.core.runner import run
from readback.core.wal import WAL
from readback.planner import plan_request

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


def test_verify_failure_compensates_every_committed_effect(adapters, root):
    """One verify fails -> all committed effects are reversed, outcome failure."""
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

    assert receipt.outcome == OUTCOME_FAILURE
    assert "notion.append_audit_row" in receipt.reason
    assert "SOMETHING ELSE ENTIRELY" in receipt.reason

    failed = [v for v in receipt.verifications if not v.passed]
    assert len(failed) == 1
    assert failed[0].app == "notion"

    # Every effect that was committed got compensated — all three, in reverse order.
    compensations = [c for c in receipt.calls if c.phase == "compensate"]
    assert [c.app for c in compensations] == ["slack", "notion", "stripe"]
    assert all(c.status in ("ok", "skipped") for c in compensations)

    # Live state is clean again.
    for adapter in adapters.values():
        assert adapter.store == {}

    records = WAL.replay(receipt.run_id, root=root)
    compensated = [r for r in records if r["state"] == wal_mod.COMPENSATED]
    assert len(compensated) == 3


def test_crash_mid_run_then_retry_does_not_double_write(adapters, root):
    """Crash after the first write, replay the WAL, retry: no effect applies twice."""
    stripe = adapters["stripe"]
    notion = adapters["notion"]

    class Boom(RuntimeError):
        pass

    # The Notion write never gets attempted: the process dies first.
    def crash(effect):
        raise Boom("process died mid-run")

    notion.apply = crash

    run_id = "run_crash_test"
    with pytest.raises(Boom):
        run(REFUND_REQUEST, adapters=adapters, run_id=run_id, root=root)

    # The Stripe refund committed before the crash.
    assert len(stripe.store) == 1
    records = WAL.replay(run_id, root=root)
    assert [r["state"] for r in records] == [
        wal_mod.INTENDED, wal_mod.COMMITTED, wal_mod.INTENDED
    ]

    # Retry the SAME run id. The WAL is replayed and the Stripe write is skipped.
    del notion.apply  # restore the real method
    receipt = run(REFUND_REQUEST, adapters=adapters, run_id=run_id, root=root)

    assert receipt.outcome == OUTCOME_SUCCESS, receipt.reason

    stripe_applies = [c for c in receipt.calls if c.app == "stripe" and c.phase == "apply"]
    assert len(stripe_applies) == 1
    assert stripe_applies[0].status == "skipped", "retry must not re-apply a committed effect"

    # The idempotency key proves it: written exactly once across both attempts.
    key = "stripe:refund:order-4417"
    assert stripe.write_count[key] == 1
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
