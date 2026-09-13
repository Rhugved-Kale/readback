"""Slack request path, with a fake Slack client and a fake runner. No network.

Exercises the four things that matter: the plan is posted before anything is
applied, the receipt is posted after, a held request posts buttons and applies
NOTHING, and approval actually executes with the approval recorded.
"""

from __future__ import annotations

import pytest

from readback.core.receipt import OUTCOME_HELD, OUTCOME_SUCCESS, ProviderCall, Receipt, Verification
from readback.slack_app import (
    ACTION_APPROVE,
    ACTION_CANCEL,
    ACTION_CONFIRM,
    SlackApp,
    _call_row,
)

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
    application._adapters = lambda run_id, injection=None: {}
    application._debug = lambda msg: None
    return application, client, runner


def _envelope(text, event_id="Ev123", user="U_HUMAN", channel=CHANNEL,
              ts="111.0", event_type="message", client_msg_id="cmid-1", **extra):
    event = {"type": event_type, "text": text, "user": user,
             "channel": channel, "ts": ts, **extra}
    if client_msg_id is not None:
        event["client_msg_id"] = client_msg_id
    return {"event_id": event_id, "event": event}


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
    assert "1. `stripe` *refund_payment* — order 4417 · $99.00" in plan_post["text"]
    assert "2. `notion` *append_audit_row* — order 4417 · refund" in plan_post["text"]
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


# -- FIX 1: event deduplication ---------------------------------------------


def test_one_message_delivered_as_two_events_runs_once(app):
    """The real bug: message.channels AND app_mention for ONE mentioned message.

    Slack delivers both, each with its own event_id. Keying dedupe on event_id
    made them look like two separate requests, so the message ran twice and the
    concurrency guard emitted "run already in progress" for the loser.

    Same channel+ts, same client_msg_id, different event_id AND different type.
    """
    application, client, runner = app
    text = f"<@{BOT}> Refund order 4417 and log the reason."
    common = dict(ts="777.0", client_msg_id="cmid-SAME")

    first = application.handle_envelope(
        _envelope(text, event_id="Ev_AAA", event_type="message", **common)
    )
    second = application.handle_envelope(
        _envelope(text, event_id="Ev_BBB", event_type="app_mention", **common)
    )

    # Exactly one of the two does the work; the other leaves no trace.
    assert {first, second} == {"ignored:mention-handled-by-app_mention", "ran:success"}

    assert len(runner.calls) == 1, "one message must execute exactly once"
    plans = [p for p in client.posts if "Plan for run" in p.get("text", "")]
    assert len(plans) == 1, "exactly one plan post"
    assert not [p for p in client.posts if "already in progress" in p.get("text", "")], (
        "the concurrency guard must never be what catches a duplicate delivery"
    )


def test_same_two_events_in_the_reverse_order_also_runs_once(app):
    """app_mention may arrive first. The deferring event must still leave no trace."""
    application, client, runner = app
    text = f"<@{BOT}> Refund order 4417 and log the reason."
    common = dict(ts="778.0", client_msg_id="cmid-REV")

    first = application.handle_envelope(
        _envelope(text, event_id="Ev_CCC", event_type="app_mention", **common)
    )
    second = application.handle_envelope(
        _envelope(text, event_id="Ev_DDD", event_type="message", **common)
    )

    assert first == "ran:success"
    assert second == "ignored:mention-handled-by-app_mention"
    assert len(runner.calls) == 1
    assert len([p for p in client.posts if "Plan for run" in p.get("text", "")]) == 1


def test_plain_retry_of_the_same_event_is_ignored(app):
    """A straight redelivery, same type, different event_id."""
    application, client, runner = app
    common = dict(ts="779.0", client_msg_id="cmid-RETRY", event_type="message")
    text = "readback: Refund order 4417 and log the reason."

    assert application.handle_envelope(
        _envelope(text, event_id="Ev_1", **common)).startswith("ran:")
    assert application.handle_envelope(
        _envelope(text, event_id="Ev_2", **common)) == "ignored:duplicate"

    assert len(runner.calls) == 1
    assert len([p for p in client.posts if "Plan for run" in p.get("text", "")]) == 1


def test_dedupe_is_not_the_concurrency_guard(app):
    """A repeat AFTER the first run finished must still be ignored.

    The in-flight lock releases when a run completes, so it cannot catch a late
    redelivery. Only message identity can.
    """
    application, _client, runner = app
    envelope = _envelope("readback: Refund order 4417 and log the reason.", ts="780.0")

    application.handle_envelope(envelope)
    assert application._in_flight is None, "run finished; the guard is no longer armed"

    assert application.handle_envelope(envelope) == "ignored:duplicate"
    assert len(runner.calls) == 1


def test_event_id_is_never_the_dedupe_key(app):
    """Two deliveries of one message differ in event_id; that must not matter."""
    from readback.slack_app import _dedupe_keys

    payload_a = _envelope("hi", event_id="Ev_X", ts="900.0", client_msg_id="cm")
    payload_b = _envelope("hi", event_id="Ev_Y", ts="900.0", client_msg_id="cm")
    keys_a = _dedupe_keys(payload_a, payload_a["event"])
    keys_b = _dedupe_keys(payload_b, payload_b["event"])

    assert keys_a == keys_b, "different event_ids must produce identical keys"
    assert all("Ev_" not in k for k in keys_a), "no key may contain an event_id"
    assert f"msg:{CHANNEL}:900.0" in keys_a


def test_client_msg_id_catches_a_repeat_with_a_different_ts(app):
    """Secondary guard: same composed message resent under a new ts."""
    application, _client, runner = app
    text = "readback: Refund order 4417 and log the reason."

    assert application.handle_envelope(
        _envelope(text, event_id="Ev_A", ts="801.0", client_msg_id="cmid-DUP")
    ).startswith("ran:")
    assert application.handle_envelope(
        _envelope(text, event_id="Ev_B", ts="802.0", client_msg_id="cmid-DUP")
    ) == "ignored:duplicate"

    assert len(runner.calls) == 1


def test_distinct_messages_are_not_deduped(app):
    """Different messages have different ts and must both run."""
    application, _client, runner = app
    application.handle_envelope(_envelope(
        "readback: Refund order 4417 and log the reason.",
        event_id="EvA", ts="811.0", client_msg_id="cmid-A"))
    application.handle_envelope(_envelope(
        "readback: Refund order 4418 and log the reason.",
        event_id="EvB", ts="812.0", client_msg_id="cmid-B"))
    assert len(runner.calls) == 2


def test_prefixed_message_without_a_mention_still_runs(app):
    """message.channels keeps handling "readback:" requests that do not mention."""
    application, _client, runner = app
    status = application.handle_envelope(_envelope(
        "readback: Refund order 4417 and log the reason.",
        event_type="message", ts="820.0", client_msg_id="cmid-P"))
    assert status.startswith("ran:")
    assert len(runner.calls) == 1


def test_dedupe_cache_is_bounded(app):
    application, _client, _runner = app
    for n in range(1300):
        application.handle_envelope(
            {"event_id": f"Ev{n}", "event": {"type": "message", "text": "hi",
                                             "user": "U_HUMAN", "channel": CHANNEL,
                                             "ts": f"{n}.0"}}
        )
    assert len(application._seen) <= 1000
    assert len(application._seen) >= 500


# -- FIX 2: the window shape reaches the risk gate ---------------------------


def _resolver(since):
    return [
        {"order_id": "4417", "amount_cents": 9900, "created": since},
        {"order_id": "4418", "amount_cents": 2900, "created": since},
        {"order_id": "4419", "amount_cents": 24900, "created": since},
        {"order_id": "9001", "amount_cents": 9900, "created": since},
        {"order_id": "9002", "amount_cents": 9900, "created": since},
        {"order_id": "5501", "amount_cents": 45000, "created": since},
    ]


def test_refund_everything_hits_the_gate_not_the_planner(app):
    application, client, runner = app
    application.order_resolver = _resolver

    status = application.handle_message(_msg("readback: Refund everything from last week."))

    assert status == "held", status
    assert runner.calls == [], "nothing may be applied"
    assert not any("no known request shape" in t.lower() for t in client.texts)

    body = " ".join(
        b["text"]["text"] for b in client.blocks() if b["type"] == "section"
    )
    assert "Held by the risk gate" in body
    assert "Unbounded scope" in body          # the rule that fired
    assert "Money limit" in body              # every OTHER rule crossed
    assert "over the limit of $500.00" in body  # the threshold
    for order in ("4417", "4418", "4419", "5501"):
        assert order in body                  # the exact order ids
    assert "$827.00" in body                  # the dollar total
    assert "2 eval-range order(s) excluded" in body  # count only, kept short
    assert len(body) < 700, "the held reply must not be truncated behind Show more"

    actions = [b for b in client.blocks() if b["type"] == "actions"]
    assert {e["action_id"] for e in actions[0]["elements"]} == {ACTION_APPROVE, ACTION_CANCEL}


def test_window_refund_excludes_eval_range_from_the_plan(app):
    application, _client, _runner = app
    application.order_resolver = _resolver
    application.handle_message(_msg("readback: Refund everything from last week."))
    held = next(iter(application._held.values()))
    ids = {e.params["order_id"] for e in held.effects}
    assert ids == {"4417", "4418", "4419", "5501"}
    assert held.enumeration["excluded_eval_orders"] == ["9001", "9002"]


def test_large_refund_plan_needs_a_second_confirmation(app):
    """One Approve click must not be able to fire six irreversible refunds."""
    application, client, runner = app
    application.order_resolver = lambda since: [
        {"order_id": str(4400 + n), "amount_cents": 9900, "created": since}
        for n in range(6)
    ]
    application.handle_message(_msg("readback: Refund everything from last week."))
    run_id = next(iter(application._held))

    first = application.handle_decision("approve", run_id, user="U_BOSS")
    assert first == "awaiting-confirmation"
    assert runner.calls == [], "first Approve must not execute a 6-refund plan"

    confirm = [b for b in client.blocks() if b["type"] == "actions"][-1]
    ids = {e["action_id"] for e in confirm["elements"]}
    assert ACTION_CONFIRM in ids
    body = " ".join(b["text"]["text"] for b in client.blocks() if b["type"] == "section")
    assert "$594.00" in body, "the second prompt must name the dollar total"

    second = application.handle_decision("approve", run_id, user="U_BOSS")
    assert second.startswith("approved:")
    assert len(runner.calls) == 1


def test_small_refund_plan_executes_on_first_approve(app):
    application, _client, runner = app
    application.order_resolver = lambda since: [
        {"order_id": "4417", "amount_cents": 60000, "created": since}
    ]
    application.handle_message(_msg("readback: Refund everything from last week."))
    run_id = next(iter(application._held))
    assert application.handle_decision("approve", run_id, user="U_BOSS").startswith("approved:")
    assert len(runner.calls) == 1


# -- FIX 3: receipt formatting ----------------------------------------------


def test_call_rows_are_fixed_width_and_truncated(app):
    from readback.core.receipt import ProviderCall

    short = ProviderCall(phase="apply", app="slack", action="post_message",
                         effect_id="e", idempotency_key="k", status="ok", latency_ms=9.5)
    longer = ProviderCall(phase="apply", app="notion", action="update_catalog_price_and_more",
                          effect_id="e", idempotency_key="k", status="irreversible",
                          latency_ms=1234.5)

    rows = [_call_row(short), _call_row(longer)]
    assert len({len(r) for r in rows}) == 1, "every row must be the same width"
    assert all(len(r) <= 46 for r in rows), "rows must fit a narrow Slack thread"
    assert "\u2026" in rows[1], "long action names truncate, never wrap"
    assert rows[0].startswith("ok"), "status leads the row"
    assert rows[0].rstrip().endswith("ms")


# -- fault injection ---------------------------------------------------------


def test_injection_suffix_is_stripped_before_planning():
    """The planned request must be identical with and without the suffix."""
    from readback.injection import parse

    clean, name = parse("move Team to $59 everywhere --inject notion_drift")
    assert clean == "move Team to $59 everywhere"
    assert name == "notion_drift"
    assert parse("move Team to $59 everywhere") == ("move Team to $59 everywhere", None)


def test_injection_is_refused_when_the_env_flag_is_unset(app, monkeypatch):
    application, client, runner = app
    monkeypatch.delenv("READBACK_ALLOW_INJECTION", raising=False)

    status = application.handle_message(
        _msg("readback: Move Pro to $79 everywhere --inject notion_drift")
    )

    assert status == "refused:injection"
    assert runner.calls == [], "nothing may run"
    assert "READBACK_ALLOW_INJECTION=1" in client.texts[0], "the rule must be named"


def test_unknown_injection_is_refused(app, monkeypatch):
    application, client, runner = app
    monkeypatch.setenv("READBACK_ALLOW_INJECTION", "1")
    status = application.handle_message(
        _msg("readback: Move Pro to $79 everywhere --inject wat")
    )
    assert status == "refused:injection"
    assert runner.calls == []
    assert "Unknown injection" in client.texts[0]


def test_injection_is_hard_refused_against_fake_adapters(monkeypatch, tmp_path):
    """The guard that keeps injection out of the eval harness permanently."""
    from readback.adapters.fake import FakeAdapter
    from readback.core.runner import run as real_run
    from readback.injection import InjectionRefused

    monkeypatch.setenv("READBACK_ALLOW_INJECTION", "1")
    fakes = {n: FakeAdapter(name=n) for n in ("stripe", "notion", "slack")}

    with pytest.raises(InjectionRefused) as exc:
        real_run("Move Pro to $79 everywhere.", adapters=fakes, root=str(tmp_path),
                 write_receipt=False, injection="notion_drift")

    assert "fake adapters" in str(exc.value)
    assert "eval harness" in str(exc.value)
    # And nothing was applied.
    assert all(a.store == {} for a in fakes.values())


def test_eval_harness_never_passes_an_injection():
    """The harness calls run() without the parameter at all."""
    import inspect

    from readback.evals import runner as eval_runner

    source = inspect.getsource(eval_runner)
    # The word appears in the harness's own prose about fault PROFILES, which
    # are a different thing. What must never appear is the kwarg.
    assert "injection=" not in source, "the eval harness must not pass injection="
    assert "injection_mod" not in source


def test_banner_appears_in_all_three_receipt_surfaces(monkeypatch):
    """Slack post, receipt.json and receipt.txt must each carry the label."""
    import json

    from readback import injection as inj
    from readback.core.receipt import Receipt
    from readback.slack_app import _receipt_message

    receipt = Receipt(run_id="run_x", requested="Move Team to $59 everywhere",
                      started_at="now")
    receipt.outcome = "failure"
    receipt.reason = "Cross-app check failed."
    receipt.injection = {
        "name": inj.NOTION_DRIFT,
        "banner": inj.banner(inj.NOTION_DRIFT),
        "describes": inj.describe(inj.NOTION_DRIFT),
    }

    expected = "FAULT INJECTED: notion_drift. Deliberate. Not a real provider failure."

    # 1. Slack
    assert expected in _receipt_message(receipt)
    # 2. JSON
    assert expected in json.dumps(receipt.to_dict())
    assert json.loads(json.dumps(receipt.to_dict()))["injection"]["name"] == "notion_drift"
    # 3. Text
    assert expected in receipt.to_text()


def test_banner_appears_on_the_slack_plan_post(app, monkeypatch):
    from readback.slack_app import _plan_message
    from readback.planner import plan_request

    plan = plan_request("Move Pro to $79 everywhere.")
    text = _plan_message("run_y", "Move Pro to $79 everywhere.", plan.effects,
                         plan.enumeration, "notion_drift")
    assert "FAULT INJECTED: notion_drift" in text
    assert "Deliberate" in text


def test_injected_notion_write_disagrees_but_verifies_on_its_own_terms():
    """Notion stays internally consistent; only a cross-app read sees the gap."""
    from readback.adapters.notion_adapter import NotionAdapter
    from readback.types import Effect

    effect = Effect(app="notion", action="update_catalog_row",
                    params={"name": "Team", "price": 59, "previous_price": 249},
                    idempotency_key="notion:catalog:team-5900")
    adapter = NotionAdapter(client=object(), run_id="r", catalog_db="c", audit_db="a",
                            injection="notion_drift")
    # Simulate what _apply_catalog does to the intended number.
    effect.prior_state = {}
    intended = adapter._price_number(effect)
    drifted = intended + 10
    effect.prior_state["injected_price"] = drifted

    assert intended == 59.0
    assert drifted == 69.0
    # verify() now expects what Notion was made to write, not what was asked --
    # so per-effect verify passes and the cross-app check is what must fail.
    assert float(effect.prior_state["injected_price"]) == 69.0
