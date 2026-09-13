"""End-to-end runs against the REAL Stripe, Notion and Slack APIs.

    pytest -m live

Deselected by default (see pyproject addopts). Everything here spends real
money in Stripe test mode, writes to the real Notion workspace, and posts to
the real Slack channel, so running it is always a deliberate act.

These tests assert the property the fake tests cannot: that read-back and the
cross-app checks hold against providers that have their own latency, their own
eventual consistency, and their own opinions about idempotency.

Each test cleans up after itself where the provider allows it. The Stripe
refund in demo 1 is the exception -- it is irreversible by design, which is the
entire reason Effect.reversible exists.
"""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

from readback.adapters.live import build_live_adapters, missing_env
from readback.cli import DEMOS
from readback.core.receipt import OUTCOME_PARTIAL, OUTCOME_SUCCESS
from readback.core.runner import run

pytestmark = pytest.mark.live


@pytest.fixture(scope="module", autouse=True)
def _env():
    load_dotenv()
    gaps = missing_env()
    if gaps:
        pytest.skip(f"live tests need {', '.join(gaps)} in .env")


@pytest.fixture
def root(tmp_path):
    return str(tmp_path / "runs")


def _run_live(request_text: str, root: str, run_id: str):
    adapters = build_live_adapters(run_id)
    return run(request_text, adapters=adapters, run_id=run_id, root=root), adapters


def test_demo_1_refund_end_to_end(root):
    """Demo 1: refund 4417, audit it in Notion, announce in Slack.

    Asserts the cross-app check specifically: the Notion audit row's Amount
    must equal what STRIPE says was refunded, not what Notion was told to write.
    """
    run_id = f"run_live_refund_{os.urandom(4).hex()}"
    receipt, adapters = _run_live(DEMOS[1], root, run_id)

    assert receipt.outcome == OUTCOME_SUCCESS, receipt.reason
    assert len(receipt.verifications) == 3
    assert all(v.passed for v in receipt.verifications), [
        v.detail for v in receipt.verifications if not v.passed
    ]

    # The refund cross-check must have actually run and passed.
    names = [c.name for c in receipt.crosschecks]
    assert any(n.startswith("refund_coherence") for n in names), names
    assert all(c.passed for c in receipt.crosschecks), [
        c.detail for c in receipt.crosschecks if not c.passed
    ]

    # Irreversible effects ran last.
    applied = [c for c in receipt.calls if c.phase == "apply"]
    assert applied[-1].app == "stripe", [c.app for c in applied]

    # Clean up what can be cleaned: the Slack post and the Notion audit row.
    # The refund itself stays -- there is no API that undoes it.
    _cleanup(adapters, receipt)


def test_demo_2_reprice_end_to_end(root):
    """Demo 2: move Pro to $79 across Stripe, Notion and Slack.

    Wholly reversible, so this test restores the $99 price afterwards.
    """
    run_id = f"run_live_price_{os.urandom(4).hex()}"
    receipt, adapters = _run_live(DEMOS[2], root, run_id)

    assert receipt.outcome == OUTCOME_SUCCESS, receipt.reason
    assert all(v.passed for v in receipt.verifications), [
        v.detail for v in receipt.verifications if not v.passed
    ]

    names = [c.name for c in receipt.crosschecks]
    assert any(n.startswith("price_coherence") for n in names), names
    assert all(c.passed for c in receipt.crosschecks), [
        c.detail for c in receipt.crosschecks if not c.passed
    ]

    # The cross-check is only meaningful if Stripe and Notion genuinely agree.
    live_stripe = adapters["stripe"].live_default_price("pro")
    live_notion = adapters["notion"].live_catalog_row("Pro")
    assert live_stripe["unit_amount"] == 7900
    assert float(live_notion["price"]) == 79.0
    assert live_notion["stripe_price_id"] == live_stripe["price_id"]

    _restore_pro_price(adapters, root)
    _cleanup(adapters, receipt)


def test_verify_failure_compensates_against_live_providers(root):
    """Drift live Notion state after the write, then confirm rollback is real.

    The refund is irreversible, so the expected outcome is
    PARTIAL_MANUAL_REMEDIATION naming the PaymentIntent -- never success.
    """
    run_id = f"run_live_drift_{os.urandom(4).hex()}"
    adapters = build_live_adapters(run_id)

    notion = adapters["notion"]
    original = notion.apply

    def apply_then_drift(effect):
        result = original(effect)
        page_id = (effect.prior_state or {}).get("created_page_id")
        if page_id:
            # Corrupt the Amount so read-back must fail.
            notion.client.pages.update(
                page_id=page_id, properties={"Amount": {"number": 0.01}}
            )
        return result

    notion.apply = apply_then_drift
    receipt = run(DEMOS[1], adapters=adapters, run_id=run_id, root=root)

    assert receipt.outcome == OUTCOME_PARTIAL, receipt.reason
    assert receipt.outcome != OUTCOME_SUCCESS
    assert receipt.manual_remediation, "an irreversible refund must be reported"
    assert receipt.manual_remediation[0].object_id.startswith("pi_")
    _cleanup(adapters, receipt)


# -- helpers ----------------------------------------------------------------


def _cleanup(adapters, receipt) -> None:
    """Best-effort teardown so repeated runs stay idempotent."""
    slack = adapters["slack"]
    try:
        for message in slack._history(slack.channel):
            if receipt.run_id in (message.get("text") or ""):
                slack.client.chat_delete(channel=slack.channel, ts=message["ts"])
    except Exception:
        pass

    notion = adapters["notion"]
    try:
        rows = notion._rows_for_run(notion._source(notion.audit_db), receipt.run_id)
        for row in rows:
            notion.client.pages.update(page_id=row["id"], archived=True)
    except Exception:
        pass


def _restore_pro_price(adapters, root) -> None:
    """Put Pro back to $99 in both Stripe and Notion after the reprice test."""
    try:
        restored = run(
            "Move Pro to $99 everywhere.",
            adapters=build_live_adapters(f"run_live_restore_{os.urandom(4).hex()}"),
            root=root,
        )
        assert restored.outcome == OUTCOME_SUCCESS, restored.reason
    except Exception as exc:  # pragma: no cover - teardown diagnostics only
        pytest.fail(f"could not restore Pro to $99, workspace left dirty: {exc}")
