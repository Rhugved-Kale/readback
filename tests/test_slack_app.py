"""Slack request path, with a fake Slack client and a fake runner. No network.

Exercises the four things that matter: the plan is posted before anything is
applied, the receipt is posted after, a held request posts buttons and applies
NOTHING, and approval actually executes with the approval recorded.
"""

from __future__ import annotations

import pytest

from readback.core.receipt import OUTCOME_HELD, OUTCOME_SUCCESS, ProviderCall, Receipt, Verification
from readback.slack_app import ACTION_APPROVE, ACTION_CANCEL, SlackApp

CHANNEL = "C_TEST"
BOT = "U_BOT"


class FakeSlackClient:
    """Records posts instead of sending them."""

    def __init__(self):
        self.posts: list[dict] = []

    def chat_postMessage(self, **kwargs):
        self.posts.append(kwargs)
        return {"ok": True, "ts": f"{1000 + len(self.posts)}.0"}

    # convenience for assertions
    @property
    def texts(self) -> list[str]:
        return [p.get("text", "") for p in self.posts]

    def blocks(self) -> list:
        return [b for p in self.posts for b in (p.get("blocks") or [])]


class FakeRunner:
    """Stands in for core.runner.run. Records every invocation."""

    def __init__(self):
        self.calls: list[dict] = []

    def __call__(self, request, adapters=None, run_id=None, root=None, approved_by=None, **kw):
        self.calls.append(
            {"request": request, "run_id": run_id, "approved_by": approved_by}
        )
        receipt = Receipt(run_id=run_id, requested=request, started_at="now")
        receipt.outcome = OUTCOME_SUCCESS
        receipt.reason = "All read-back assertions passed."
        receipt.calls = [
            ProviderCall(
                phase="apply", app="stripe", action="refund_payment",
                effect_id="e1", idempotency_key="k1", status="ok", latency_ms=12.5,
            )
        ]
        receipt.verifications = [
            Verification(app="stripe", action="refund_payment", effect_id="e1",
                         passed=True, detail="live read confirms refunded=9900")
        ]
        if approved_by:
            receipt.approval = {"approver": approved_by, "gate_reason": "Money limit"}
        return receipt


@pytest.fixture
def app():
    client = FakeSlackClient()
    runner = FakeRunner()
    # Adapters are never built in these tests: the fake runner replaces the
    # only thing that would use them.
    application = SlackApp(client=client, channel=CHANNEL, bot_user_id=BOT, runner=runner)
    application._adapters = lambda run_id: {}
    return application, client, runner


def _msg(text, user="U_HUMAN", channel=CHANNEL, **extra):
    return {"type": "message", "text": text, "user": user, "channel": channel,
            "ts": "111.0", **extra}


def test_plan_then_receipt_are_both_posted(app):
    application, client, runner = app

    status = application.handle_message(_msg("readback: Refund order 4417 and log the reason."))

    assert status.startswith("ran:"), status
    assert len(runner.calls) == 1

    plan_post, receipt_post = client.posts[0], client.posts[-1]

    # The plan goes out BEFORE execution, numbered, with app and action.
    assert "Plan for run" in plan_post["text"]
    assert "1. `stripe` · *refund_payment*" in plan_post["text"]
    assert "2. `notion` · *append_audit_row*" in plan_post["text"]
    assert plan_post["thread_ts"] == "111.0"

    # The receipt follows, with outcome header, calls and assertions.
    assert "SUCCESS" in receipt_post["text"]
    assert "Provider calls" in receipt_post["text"]
    assert "```" in receipt_post["text"]
    assert "PASS" in receipt_post["text"]
    assert receipt_post["thread_ts"] == "111.0"


def test_bot_and_foreign_channel_messages_are_ignored(app):
    application, client, runner = app

    assert application.handle_message(_msg("readback: x", bot_id="B1")) == "ignored:bot"
    assert application.handle_message(_msg("readback: x", user=BOT)) == "ignored:self"
    assert application.handle_message(_msg("readback: x", channel="C_OTHER")) == "ignored:channel"
    assert application.handle_message(_msg("just chatting")) == "ignored:no-trigger"

    assert client.posts == []
    assert runner.calls == []


def test_mention_triggers_and_prefix_triggers(app):
    application, _client, runner = app
    application.handle_message(_msg(f"<@{BOT}> Refund order 4417 and log the reason."))
    assert len(runner.calls) == 1
    assert runner.calls[0]["request"] == "Refund order 4417 and log the reason."


def test_held_request_posts_buttons_and_executes_nothing(app):
    application, client, runner = app

    status = application.handle_message(
        _msg("readback: Archive the 9 cancelled Q3 orders and post a summary.")
    )

    assert status == "held"
    assert runner.calls == [], "a held plan must not execute"

    blocks = client.blocks()
    actions = [b for b in blocks if b["type"] == "actions"]
    assert actions, "held request must post an actions block"
    action_ids = {e["action_id"] for e in actions[0]["elements"]}
    assert action_ids == {ACTION_APPROVE, ACTION_CANCEL}

    # The exact rule and threshold are named.
    body = " ".join(
        b["text"]["text"] for b in blocks if b["type"] == "section"
    )
    assert "Record-count limit" in body
    assert "over the limit of 5" in body


def test_approval_executes_and_records_the_approver(app):
    application, client, runner = app
    application.handle_message(
        _msg("readback: Archive the 9 cancelled Q3 orders and post a summary.")
    )
    run_id = next(iter(application._held))

    status = application.handle_decision("approve", run_id, user="U_BOSS")

    assert status.startswith("approved:"), status
    assert len(runner.calls) == 1
    assert runner.calls[0]["approved_by"] == "slack:U_BOSS"
    assert runner.calls[0]["run_id"] == run_id
    assert application._held == {}
    assert any("Approved" in t for t in client.texts)
    assert any("Released by slack:U_BOSS" in t for t in client.texts)


def test_cancel_discards_without_executing(app):
    application, client, runner = app
    application.handle_message(
        _msg("readback: Archive the 9 cancelled Q3 orders and post a summary.")
    )
    run_id = next(iter(application._held))

    assert application.handle_decision("cancel", run_id, user="U_BOSS") == "cancelled"
    assert runner.calls == []
    assert application._held == {}
    assert any("Cancelled" in t for t in client.texts)


def test_plain_text_approval_fallback_works_in_thread(app):
    """The Block Kit fallback: 'approve {run_id}' typed in the thread."""
    application, _client, runner = app
    application.handle_message(
        _msg("readback: Archive the 9 cancelled Q3 orders and post a summary.")
    )
    run_id = next(iter(application._held))

    status = application.handle_message(_msg(f"approve {run_id}", user="U_BOSS"))

    assert status.startswith("approved:"), status
    assert runner.calls[0]["approved_by"] == "slack:U_BOSS"


def test_eval_range_orders_are_refused(app):
    application, client, runner = app

    status = application.handle_message(_msg("readback: Refund order 9001 and log the reason."))

    assert status == "refused:eval-order"
    assert runner.calls == []
    text = client.texts[0]
    assert "9001" in text
    assert "9001-9020" in text
    # Demo orders are unaffected.
    assert application._eval_order_guard("Refund order 4417") is None


def test_second_request_while_one_is_in_flight_is_told_to_wait(app):
    application, client, runner = app
    application._in_flight = "run_already_going"

    status = application.handle_message(_msg("readback: Refund order 4417 and log the reason."))

    assert status == "busy"
    assert runner.calls == []
    assert "run_already_going" in client.texts[0]


def test_unparseable_request_is_refused_not_executed(app):
    application, client, runner = app
    status = application.handle_message(_msg("readback: do something vague"))
    assert status == "refused:planner"
    assert runner.calls == []
    assert "Refused" in client.texts[0]
