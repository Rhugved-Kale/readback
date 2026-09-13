"""End-to-end runs against the REAL Stripe, Notion and Slack APIs.

    pytest -m live

Deselected by default (see pyproject addopts). Everything here spends real
money in Stripe test mode, writes to the real Notion workspace, and posts to
the real Slack channel, so running it is always a deliberate act.

These tests assert the property the fake tests cannot: that read-back and the
cross-app checks hold against providers that have their own latency, their own
eventual consistency, and their own opinions about idempotency.

TEST DATA ONLY. These run against order 9001 (the 9001-9020 test range) and the
TEAM product. Never 4417-4419 and never Pro -- those are the demo's, and a
refund cannot be undone, so a test pointed at them costs a re-shoot. Replenish
the range with `python -m readback.seed --orders 9001-9020`.

Each test cleans up after itself where the provider allows it. The Stripe refund
is the exception -- it is irreversible by design, which is the entire reason
Effect.reversible exists, and why it is aimed at a disposable order.
"""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

from readback.adapters.live import build_live_adapters, missing_env
from readback.adapters.stripe_adapter import find_payment_intents_by_order
from readback.core.receipt import OUTCOME_PARTIAL, OUTCOME_SUCCESS
from readback.core.runner import run

pytestmark = pytest.mark.live

#: The disposable product these tests are allowed to touch.
#:
#: Refund orders are NOT hardcoded. A refund is irreversible, so a fixed order
#: is single-use: the first run refunds it and every run after that re-refunds
#: an already-refunded charge. Stripe rejects the duplicate, but verify() still
#: passes -- the order really is refunded, just by an earlier run -- so the test
#: goes green while exercising nothing. That is the failure mode this whole
#: project exists to catch, and it bit the suite itself.
#:
#: So each test CLAIMS a fresh unrefunded order from the 9001-9020 pool at run
#: time. Two per full suite run; replenish with
#: `python -m readback.seed --orders 9001-9020`.
TEST_ORDER_LOW, TEST_ORDER_HIGH = 9001, 9020
TEST_PRODUCT_KEY = "team"
TEST_PRODUCT_DISPLAY = "Team"
TEST_PRODUCT_BASE_DOLLARS = 249
TEST_PRODUCT_NEW_DOLLARS = 279

REPRICE_REQUEST = f"Move {TEST_PRODUCT_DISPLAY} to ${TEST_PRODUCT_NEW_DOLLARS} everywhere."
RESTORE_REQUEST = f"Move {TEST_PRODUCT_DISPLAY} to ${TEST_PRODUCT_BASE_DOLLARS} everywhere."


def _unrefunded_orders() -> list[str]:
    """Every order in the pool whose payment is still refundable.

    Reads Stripe live rather than tracking state locally: the pool is shared
    with the eval harness and with whoever ran the suite last.
    """
    import stripe as stripe_sdk

    stripe_sdk.api_key = os.environ["STRIPE_SECRET_KEY"]
    usable = []
    for number in range(TEST_ORDER_LOW, TEST_ORDER_HIGH + 1):
        order_id = str(number)
        for intent in find_payment_intents_by_order(stripe_sdk, order_id):
            if intent.status != "succeeded":
                continue
            refunded = sum(
                int(r.amount)
                for r in stripe_sdk.Refund.list(payment_intent=intent.id, limit=100).data
                if r.status == "succeeded"
            )
            if refunded == 0:
                usable.append(order_id)
                break
    return usable


@pytest.fixture(scope="module")
def order_pool() -> list[str]:
    """Unrefunded test orders, queried once per session."""
    pool = _unrefunded_orders()
    if len(pool) < 2:
        pytest.skip(
            f"only {len(pool)} unrefunded order(s) left in {TEST_ORDER_LOW}-{TEST_ORDER_HIGH}; "
            f"run `python -m readback.seed --orders "
            f"{TEST_ORDER_LOW}-{TEST_ORDER_HIGH}` to replenish"
        )
    return pool


@pytest.fixture
def fresh_order(order_pool) -> str:
    """Claim one unrefunded order, so no two tests share a refund target."""
    return order_pool.pop(0)


@pytest.fixture(scope="module", autouse=True)
def _env():
    load_dotenv()
    gaps = missing_env()
    if gaps:
        pytest.skip(f"live tests need {', '.join(gaps)} in .env")


@pytest.fixture
def root():
    """Persistent receipt directory.

    Deliberately not tmp_path: a live run's receipt is the artifact you read
    afterwards to see what actually happened to real money. Throwing it away
    with the temp dir would defeat the point of writing one. runs/ is gitignored.
    """
    return "runs/live"


def _run_live(request_text: str, root: str, run_id: str):
    adapters = build_live_adapters(run_id)
    return run(request_text, adapters=adapters, run_id=run_id, root=root), adapters


def test_refund_end_to_end(root, fresh_order):
    """Refund a freshly claimed test order, audit it in Notion, announce in Slack.

    Asserts the cross-app check specifically: the Notion audit row's Amount
    must equal what STRIPE says was refunded, not what Notion was told to write.
    """
    run_id = f"run_live_refund_{os.urandom(4).hex()}"
    request = f"Refund order {fresh_order} and log the reason."
    receipt, adapters = _run_live(request, root, run_id)

    # The refund must have been performed BY THIS RUN, not inherited from an
    # earlier one that already spent the order.
    stripe_apply = [
        c for c in receipt.calls if c.app == "stripe" and c.phase == "apply"
    ]
    assert stripe_apply and stripe_apply[0].status == "ok", (
        f"refund apply did not succeed on a fresh order: "
        f"{stripe_apply[0].error if stripe_apply else 'no stripe call'}"
    )

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


def test_reprice_end_to_end(root):
    """Move Team to $279 across Stripe, Notion and Slack.

    Wholly reversible, so this test restores the $249 price afterwards.
    Deliberately Team and not Pro: Pro is what the demo reprices.
    """
    run_id = f"run_live_price_{os.urandom(4).hex()}"
    receipt, adapters = _run_live(REPRICE_REQUEST, root, run_id)

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
    live_stripe = adapters["stripe"].live_default_price(TEST_PRODUCT_KEY)
    live_notion = adapters["notion"].live_catalog_row(TEST_PRODUCT_DISPLAY)
    assert live_stripe["unit_amount"] == TEST_PRODUCT_NEW_DOLLARS * 100
    assert float(live_notion["price"]) == float(TEST_PRODUCT_NEW_DOLLARS)
    assert live_notion["stripe_price_id"] == live_stripe["price_id"]

    _restore_test_product_price(root)
    _cleanup(adapters, receipt)


def test_verify_failure_compensates_against_live_providers(root, fresh_order):
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
    request = f"Refund order {fresh_order} and log the reason."
    receipt = run(request, adapters=adapters, run_id=run_id, root=root)

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


def _restore_test_product_price(root) -> None:
    """Put Team back to $249 in both Stripe and Notion after the reprice test."""
    try:
        restored = run(
            RESTORE_REQUEST,
            adapters=build_live_adapters(f"run_live_restore_{os.urandom(4).hex()}"),
            root=root,
        )
        assert restored.outcome == OUTCOME_SUCCESS, restored.reason
    except Exception as exc:  # pragma: no cover - teardown diagnostics only
        pytest.fail(
            f"could not restore {TEST_PRODUCT_DISPLAY} to "
            f"${TEST_PRODUCT_BASE_DOLLARS}, workspace left dirty: {exc}"
        )
