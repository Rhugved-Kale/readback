"""Slack interface: request in, plan posted, receipt posted, approval in-channel.

    python -m readback.slack_app

Listens on SLACK_CHANNEL_ID via Socket Mode. Triggers on a message that
@mentions the bot, or any message starting with "readback:".

The handler logic is deliberately separated from the Socket Mode transport:
`SlackApp` takes a `client` (anything with chat_postMessage) and a `runner`
callable, so the whole request path is testable with no network and no tokens.
`main()` is the only part that touches a socket.
"""

from __future__ import annotations

import os
import re
import threading
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from .core.receipt import (
    OUTCOME_FAILURE,
    OUTCOME_HELD,
    OUTCOME_PARTIAL,
    OUTCOME_REFUSED,
    OUTCOME_SUCCESS,
    Receipt,
)
from . import injection as injection_mod
from .core.runner import run as run_request
from .planner import plan_request
from .core import riskgate

#: Orders reserved for the eval harness. A Slack request naming one is refused:
#: those payments are consumed by `pytest -m live` and the eval matrix, and a
#: refund cannot be undone, so a human refunding one by hand breaks a suite
#: that has no way to know it happened.
EVAL_ORDER_LOW, EVAL_ORDER_HIGH = 9001, 9020

TRIGGER_PREFIX = "readback:"

#: Plain-text fallback for the approval gate, accepted in-thread alongside the
#: Block Kit buttons: "approve run_abc123" / "cancel run_abc123".
_DECISION_RE = re.compile(r"^\s*(approve|cancel)\s+(?P<run_id>[\w-]+)\s*$", re.IGNORECASE)

ACTION_APPROVE = "readback_approve"
ACTION_CANCEL = "readback_cancel"
ACTION_CONFIRM = "readback_confirm"

#: How many event ids to remember for deduplication.
DEDUPE_CAPACITY = 1000

#: Refund count above which a single Approve click is not enough.
DOUBLE_CONFIRM_REFUNDS = 5

#: Column widths for the receipt's call table. Slack threads are narrow and a
#: code block does not wrap gracefully -- it breaks columns apart mid-row -- so
#: every line is built to fit rather than relying on the client.
_ACTION_WIDTH = 22


@dataclass
class HeldRun:
    """A plan the risk gate stopped, waiting on a human."""

    run_id: str
    request: str
    channel: str
    thread_ts: str
    gate_reason: str
    requester: str
    effects: list = field(default_factory=list)
    enumeration: dict = field(default_factory=dict)
    crossed: list = field(default_factory=list)
    #: Set once a human has clicked Approve on a large refund plan and is being
    #: asked to confirm the dollar total.
    awaiting_confirmation: bool = False

    @property
    def refund_count(self) -> int:
        return sum(1 for e in self.effects if e.action == "refund_payment")

    @property
    def total_cents(self) -> int:
        return sum(getattr(e, "money_cents", 0) for e in self.effects)


@dataclass
class SlackApp:
    """Request handling, independent of the Socket Mode transport."""

    client: Any
    channel: str
    bot_user_id: str = ""
    runner: Callable[..., Receipt] = run_request
    root: str = "runs"
    #: READ-ONLY Stripe enumeration for time-window refunds. None keeps the
    #: planner offline.
    order_resolver: Callable[[datetime], list[dict]] | None = None

    #: One run at a time. Ops writes against three live systems should never
    #: interleave: two concurrent repricings would each verify a world the
    #: other is still changing, and rollback order would be undefined.
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _in_flight: str | None = field(default=None, init=False)
    _held: dict[str, HeldRun] = field(default_factory=dict, init=False)

    #: Bounded LRU of Slack event ids already handled.
    #:
    #: Slack redelivers event envelopes -- the same logical event arrives more
    #: than once, with a different envelope_id. Without this, one message was
    #: being planned and executed twice; the concurrency guard sometimes caught
    #: the second one, which MASKED the bug rather than fixing it (and when the
    #: first run had already finished, nothing caught it at all).
    #:
    #: Keyed on event_id, falling back to client_msg_id, falling back to
    #: channel+ts, because a retry preserves all three while envelope_id
    #: changes.
    _seen: OrderedDict = field(default_factory=OrderedDict, init=False)
    _seen_lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _debug: Callable[[str], None] = print

    # -- entry points ------------------------------------------------------

    def handle_envelope(self, payload: dict) -> str | None:
        """Entry point for an Events API payload, with deduplication.

        The envelope is acknowledged by the caller BEFORE this runs, so a slow
        run cannot trigger Slack's 3-second retry.
        """
        event = (payload or {}).get("event", {}) or {}

        self._debug(
            "[inbound] type=%s event_id=%s client_msg_id=%s channel=%s ts=%s"
            % (
                event.get("type"),
                (payload or {}).get("event_id"),
                event.get("client_msg_id"),
                event.get("channel"),
                event.get("ts"),
            )
        )

        # Stand-down BEFORE claiming a dedupe key.
        #
        # Exactly one subscription may claim a mentioned message: Slack sends
        # both a message.channels and an app_mention event for it, and
        # app_mention is the more specific one. message.channels still handles
        # "readback:" requests that do not mention the bot.
        #
        # The order matters and is easy to get wrong: claiming the key first
        # meant the deferring message event burned the key, and the app_mention
        # that was supposed to do the work was then rejected as that key's
        # duplicate -- so the request ran ZERO times instead of twice. A
        # deferred event must leave no trace.
        if self._defers_to_app_mention(event):
            self._debug(
                f"[defer] message event for {event.get('channel')}:{event.get('ts')} "
                f"mentions the bot; leaving it to app_mention"
            )
            return "ignored:mention-handled-by-app_mention"

        keys = _dedupe_keys(payload, event)
        if keys:
            with self._seen_lock:
                hit = next((k for k in keys if k in self._seen), None)
                if hit is not None:
                    self._seen.move_to_end(hit)
                    self._debug(
                        f"[dedupe] ignoring repeat delivery of {hit} "
                        f"(type={event.get('type')})"
                    )
                    return "ignored:duplicate"
                for key in keys:
                    self._seen[key] = True
                while len(self._seen) > DEDUPE_CAPACITY:
                    self._seen.popitem(last=False)

        return self.handle_message(event)

    def _defers_to_app_mention(self, event: dict) -> bool:
        """True for a message.channels event that app_mention will also deliver."""
        if event.get("type") != "message":
            return False
        if not self.bot_user_id:
            return False
        return f"<@{self.bot_user_id}>" in (event.get("text") or "")

    def handle_message(self, event: dict) -> str | None:
        """Route one Slack message event. Returns a short status for tests."""
        if event.get("bot_id") or event.get("subtype") == "bot_message":
            return "ignored:bot"
        if self.bot_user_id and event.get("user") == self.bot_user_id:
            return "ignored:self"
        if event.get("channel") != self.channel:
            return "ignored:channel"

        text = (event.get("text") or "").strip()
        if not text:
            return "ignored:empty"

        thread_ts = event.get("thread_ts") or event.get("ts")

        decision = _DECISION_RE.match(_strip_mention(text, self.bot_user_id))
        if decision:
            return self.handle_decision(
                decision.group(1).lower(),
                decision.group("run_id"),
                user=event.get("user", "someone"),
            )

        if not self._is_trigger(text):
            return "ignored:no-trigger"

        request = _clean_request(text, self.bot_user_id)
        if not request:
            return "ignored:empty-request"

        return self.handle_request(request, thread_ts, event.get("user", "someone"))

    def handle_request(self, request: str, thread_ts: str, user: str) -> str:
        # Strip any `--inject <name>` suffix BEFORE anything else sees the text,
        # so the planned request is byte-identical to the same request without
        # it. The injection changes how a provider behaves, never what was asked.
        request, injection = injection_mod.parse(request)

        if injection:
            refusal = injection_mod.refusal_reason(injection)
            if refusal:
                self._post(thread_ts, f":no_entry: *Injection refused*\n>{refusal}")
                return "refused:injection"

        blocked = self._eval_order_guard(request)
        if blocked:
            self._post(thread_ts, blocked)
            return "refused:eval-order"

        with self._lock:
            if self._in_flight:
                self._post(
                    thread_ts,
                    f":hourglass: A run is already in progress (`{self._in_flight}`). "
                    f"One run at a time — try again once it reports back.",
                )
                return "busy"
            run_id = f"run_{uuid.uuid4().hex[:12]}"
            self._in_flight = run_id

        try:
            plan = plan_request(request, order_resolver=self.order_resolver)

            # The GATE is consulted before the planner's refusal, matching the
            # runner. A request the gate holds must be reported as held even
            # when the planner could not build a plan for it -- otherwise
            # "refund everything from last week" comes back as a parse failure
            # and the risk rule that actually applies is never shown.
            gate = riskgate.evaluate(request, plan.effects)

            if gate.held:
                self._post(thread_ts, _plan_message(run_id, request, plan.effects, plan.enumeration))
                self._held[run_id] = HeldRun(
                    run_id=run_id, request=request, channel=self.channel,
                    thread_ts=thread_ts, gate_reason=gate.reason, requester=user,
                    effects=list(plan.effects), enumeration=plan.enumeration,
                    crossed=list(gate.crossed),
                )
                self._post_blocks(
                    thread_ts,
                    text=f"Held for approval — run {run_id}",
                    blocks=_hold_blocks(run_id, gate, plan.effects, plan.enumeration),
                )
                return "held"

            if plan.refused or not plan.effects:
                reason = plan.refusal or "The planner produced no effects for this request."
                self._post(thread_ts, f"*Refused* — run `{run_id}`\n>{reason}")
                return "refused:planner"

            self._post(
                thread_ts,
                _plan_message(run_id, request, plan.effects, plan.enumeration, injection),
            )

            receipt = self.runner(
                request, adapters=self._adapters(run_id, injection), run_id=run_id,
                root=self.root, order_resolver=self.order_resolver, injection=injection,
            )
            self._post(thread_ts, _receipt_message(receipt))
            return f"ran:{receipt.outcome}"
        finally:
            with self._lock:
                if self._in_flight == run_id and run_id not in self._held:
                    self._in_flight = None

    def handle_decision(self, decision: str, run_id: str, user: str) -> str:
        """Approve or cancel a held run, from a button or a plain-text reply."""
        held = self._held.get(run_id)
        if held is None:
            self._post(None, f"No held run `{run_id}` is waiting for a decision.")
            return "unknown-run"

        if decision == "cancel":
            self._held.pop(run_id, None)
            with self._lock:
                if self._in_flight == run_id:
                    self._in_flight = None
            self._post(
                held.thread_ts,
                f":x: *Cancelled* — run `{run_id}` discarded by <@{user}>. "
                f"Nothing was applied.",
            )
            return "cancelled"

        # A large refund plan takes TWO deliberate clicks. Refunds are
        # irreversible: one stray tap on a phone should not be able to move
        # real money across a dozen customers. The second prompt names the
        # dollar total, because "Approve" alone does not tell you what you are
        # approving.
        if (
            decision == "approve"
            and not held.awaiting_confirmation
            and held.refund_count > DOUBLE_CONFIRM_REFUNDS
        ):
            held.awaiting_confirmation = True
            self._held[run_id] = held
            self._post_blocks(
                held.thread_ts,
                text=f"Confirm {held.refund_count} refunds — run {run_id}",
                blocks=_confirm_blocks(run_id, held),
            )
            return "awaiting-confirmation"

        self._held.pop(run_id, None)
        try:
            self._post(
                held.thread_ts,
                f":white_check_mark: *Approved* by <@{user}> — executing run `{run_id}`.",
            )
            receipt = self.runner(
                held.request,
                adapters=self._adapters(run_id),
                run_id=run_id,
                root=self.root,
                approved_by=f"slack:{user}",
                order_resolver=self.order_resolver,
            )
            self._post(held.thread_ts, _receipt_message(receipt))
            return f"approved:{receipt.outcome}"
        finally:
            with self._lock:
                if self._in_flight == run_id:
                    self._in_flight = None

    # -- helpers -----------------------------------------------------------

    def _adapters(self, run_id: str, injection: str | None = None) -> dict[str, Any]:
        from .adapters.live import build_live_adapters

        return build_live_adapters(run_id, injection=injection)

    def _is_trigger(self, text: str) -> bool:
        if text.lower().startswith(TRIGGER_PREFIX):
            return True
        return bool(self.bot_user_id) and f"<@{self.bot_user_id}>" in text

    def _eval_order_guard(self, request: str) -> str | None:
        hits = sorted(
            {
                number
                for number in re.findall(r"\b(\d{4})\b", request)
                if EVAL_ORDER_LOW <= int(number) <= EVAL_ORDER_HIGH
            }
        )
        if not hits:
            return None
        return (
            f":no_entry: *Refused* — order(s) {', '.join(hits)} are in the reserved "
            f"eval range `{EVAL_ORDER_LOW}-{EVAL_ORDER_HIGH}`.\n"
            f">Those payments are consumed by the eval harness and the live test "
            f"suite. A refund cannot be undone, so refunding one by hand would "
            f"break a suite that has no way to know it happened."
        )

    def _post(self, thread_ts: str | None, text: str) -> None:
        kwargs = {"channel": self.channel, "text": text}
        if thread_ts:
            kwargs["thread_ts"] = thread_ts
        self.client.chat_postMessage(**kwargs)

    def _post_blocks(self, thread_ts: str | None, text: str, blocks: list) -> None:
        kwargs = {"channel": self.channel, "text": text, "blocks": blocks}
        if thread_ts:
            kwargs["thread_ts"] = thread_ts
        self.client.chat_postMessage(**kwargs)


# -- message formatting ------------------------------------------------------


def _strip_mention(text: str, bot_user_id: str) -> str:
    if bot_user_id:
        text = text.replace(f"<@{bot_user_id}>", " ")
    return text.strip()


def _clean_request(text: str, bot_user_id: str) -> str:
    text = _strip_mention(text, bot_user_id)
    if text.lower().startswith(TRIGGER_PREFIX):
        text = text[len(TRIGGER_PREFIX):]
    return text.strip()


def _dedupe_keys(payload: dict, event: dict) -> list[str]:
    """Identity of the MESSAGE, not of the envelope that carried it.

    ONE Slack message can arrive as SEVERAL events. Subscribed to both
    message.channels and app_mention, a mentioned message is delivered twice --
    once per subscription -- each with its own `event_id`. Keying on event_id
    therefore treats one message as two distinct requests, which is exactly
    what happened: two runs from one mention, with the concurrency guard
    producing a "run already in progress" reply for the loser.
    
    `event_id` is deliberately NOT used, primary or otherwise. Neither is
    `envelope_id`, which changes on every retry. What is stable across both
    redelivery AND multi-subscription fan-out is the message itself:
    channel + ts, with client_msg_id as a secondary guard for the case where a
    client resends the same composed message.
    
    Returns every key this message is known by; a hit on ANY of them is a
    duplicate.
    """
    keys: list[str] = []
    channel, ts = event.get("channel"), event.get("ts")
    if channel and ts:
        keys.append(f"msg:{channel}:{ts}")
    client_msg_id = event.get("client_msg_id")
    if client_msg_id:
        keys.append(f"client:{client_msg_id}")
    return keys


def _money(cents: int) -> str:
    return f"${cents / 100:,.2f}"


def _short_rule(rule: str) -> str:
    """The headline clause of a gate rule, without the explanatory tail."""
    head = rule.split(". A human")[0].split(", which names")[0]
    return head.rstrip(".") + "."


def _effect_target(effect) -> str:
    """What this effect acts ON, for the plan post.

    "1. stripe refund_payment / 2. stripe refund_payment" tells a viewer
    nothing -- the two lines are indistinguishable. A judge watching the video
    has to be able to read the plan and see which order, which product, which
    price.
    """
    params = effect.params or {}
    action = effect.action

    if action in ("refund_payment", "archive_order"):
        order = params.get("order_id", "?")
        cents = params.get("amount_cents")
        return f"order {order}" + (f" · {_money(int(cents))}" if cents else "")

    if action in ("create_price", "update_price"):
        key = params.get("product_key", "?")
        cents = params.get("unit_amount_cents") or params.get("new_amount_cents") or 0
        return f"{str(key).capitalize()} → {_money(int(cents))}/mo"

    if action in ("update_catalog_row", "update_catalog_price"):
        name = params.get("product_name") or params.get("name") or "?"
        price = params.get("new_price", params.get("price"))
        return f"{name} row → ${price}"

    if action == "append_audit_row":
        return f"order {params.get('order_id', '?')} · {params.get('kind', 'entry')}"

    if action == "post_message":
        text = str(params.get("text") or "").splitlines()[0]
        return f"“{text[:44]}{'…' if len(text) > 44 else ''}”"

    return ", ".join(f"{k}={v}" for k, v in list(params.items())[:2]) or "—"


def _plan_message(
    run_id: str,
    request: str,
    effects: list,
    enumeration: dict | None = None,
    injection: str | None = None,
) -> str:
    lines = []
    if injection:
        lines += [
            f":test_tube: *{injection_mod.banner(injection)}*",
            f">_{injection_mod.describe(injection)}_",
            "",
        ]
    lines += [f"*Plan for run* `{run_id}`", f">{request}", ""]
    if not effects:
        lines.append("_No effects planned._")
    for index, effect in enumerate(effects, 1):
        lines.append(
            f"{index}. `{effect.app}` *{effect.action}* — {_effect_target(effect)}"
        )

    enumeration = enumeration or {}
    if enumeration.get("resolved"):
        excluded = enumeration.get("excluded_count", 0)
        lines += [
            "",
            f"_Enumerated {len(enumeration.get('order_ids', []))} order(s) from the "
            f"{enumeration.get('window')}, totalling "
            f"{_money(enumeration.get('total_cents', 0))}._",
        ]
        if excluded:
            lines.append(
                f"_Excluded {excluded} eval-range order(s) "
                f"({', '.join(enumeration.get('excluded_eval_orders', []))}) — "
                f"reserved for the eval harness._"
            )
    return "\n".join(lines)


def _hold_blocks(run_id: str, gate, effects: list, enumeration: dict | None = None) -> list:
    enumeration = enumeration or {}
    total_cents = sum(getattr(e, "money_cents", 0) for e in effects)
    order_ids = enumeration.get("order_ids") or [
        str(e.params.get("order_id")) for e in effects if e.params.get("order_id")
    ]

    # Kept deliberately short: Slack collapses a long thread message behind
    # "Show more", which would hide the buttons and the dollar total -- the two
    # things the human is being asked to act on. Rules are condensed to their
    # headline clause, excluded orders to a count.
    crossed = gate.crossed or [gate.reason]
    body = [f":warning: *Held by the risk gate* — run `{run_id}`", ""]
    for rule in crossed:
        body.append(f"• {_short_rule(rule)}")

    body.append("")
    if order_ids:
        shown = order_ids[:10]
        suffix = f" +{len(order_ids) - len(shown)} more" if len(order_ids) > len(shown) else ""
        body.append(
            f"*Would refund {len(order_ids)} order(s) · {_money(total_cents)}*"
        )
        body.append("`" + "`, `".join(shown) + "`" + suffix)
    else:
        body.append("*No effects enumerated.*")

    if enumeration.get("excluded_count"):
        body.append(f"_{enumeration['excluded_count']} eval-range order(s) excluded._")

    body.append("*Nothing applied.*")

    return [
        {"type": "section", "text": {"type": "mrkdwn", "text": "\n".join(body)}},
        {
            "type": "actions",
            "block_id": f"readback_gate:{run_id}",
            "elements": [
                {
                    "type": "button",
                    "style": "primary",
                    "text": {"type": "plain_text", "text": "Approve"},
                    "action_id": ACTION_APPROVE,
                    "value": run_id,
                },
                {
                    "type": "button",
                    "style": "danger",
                    "text": {"type": "plain_text", "text": "Cancel"},
                    "action_id": ACTION_CANCEL,
                    "value": run_id,
                },
            ],
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Or reply in thread: `approve {run_id}` / `cancel {run_id}`",
                }
            ],
        },
    ]


_OUTCOME_HEADER = {
    OUTCOME_SUCCESS: ":large_green_circle: *SUCCESS*",
    OUTCOME_FAILURE: ":red_circle: *FAILURE — all committed effects reversed*",
    OUTCOME_PARTIAL: ":rotating_light: *PARTIAL — MANUAL REMEDIATION REQUIRED*",
    OUTCOME_HELD: ":warning: *HELD*",
    OUTCOME_REFUSED: ":no_entry: *REFUSED*",
}


def _confirm_blocks(run_id: str, held: HeldRun) -> list:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f":rotating_light: *Second confirmation required* — run `{run_id}`\n"
                    f"This approves *{held.refund_count} refunds* totalling "
                    f"*{_money(held.total_cents)}*.\n"
                    f"Refunds cannot be undone. Confirm only if that total is right."
                ),
            },
        },
        {
            "type": "actions",
            "block_id": f"readback_confirm:{run_id}",
            "elements": [
                {
                    "type": "button",
                    "style": "danger",
                    "text": {
                        "type": "plain_text",
                        "text": f"Yes, refund {_money(held.total_cents)}",
                    },
                    "action_id": ACTION_CONFIRM,
                    "value": run_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Cancel"},
                    "action_id": ACTION_CANCEL,
                    "value": run_id,
                },
            ],
        },
    ]


def _call_row(call) -> str:
    """One provider call on one line, built to fit a narrow Slack thread.

    Status first because it is what the eye scans for, then the action, then
    the latency right-aligned. Long action names are truncated rather than
    allowed to wrap: a wrapped row breaks the columns apart and makes the whole
    block unreadable, which is what it was doing before.
    """
    action = f"{call.app}.{call.action}"
    if len(action) > _ACTION_WIDTH:
        action = action[: _ACTION_WIDTH - 1] + "\u2026"
    return f"{call.status[:11]:<11} {action:<{_ACTION_WIDTH}} {call.latency_ms:>8.1f}ms"


def _receipt_message(receipt: Receipt) -> str:
    lines = []
    if receipt.injection:
        lines += [
            f":test_tube: *{receipt.injection.get('banner', '')}*",
            f">_{receipt.injection.get('describes', '')}_",
            "",
        ]
    lines += [
        f"{_OUTCOME_HEADER.get(receipt.outcome, receipt.outcome.upper())} — run `{receipt.run_id}`",
        f">{receipt.reason}",
    ]

    if receipt.approval:
        lines.append(
            f">_Released by {receipt.approval['approver']} despite: "
            f"{receipt.approval.get('gate_reason', '')}_"
        )

    if receipt.calls:
        for phase in ("apply", "compensate"):
            phase_calls = [c for c in receipt.calls if c.phase == phase]
            if not phase_calls:
                continue
            lines += ["", f"*Provider calls — {phase}*", "```"]
            for call in phase_calls:
                lines.append(_call_row(call))
            lines.append("```")
            for call in phase_calls:
                if call.error:
                    lines.append(f"> `{call.app}.{call.action}` — {call.error[:150]}")

    if receipt.verifications:
        lines += ["", "*Read-back assertions*"]
        for check in receipt.verifications:
            mark = ":white_check_mark: PASS" if check.passed else ":x: FAIL"
            lines.append(f"{mark} `{check.app}.{check.action}`")
            lines.append(f">{check.detail[:280]}")

    if receipt.crosschecks:
        lines += ["", "*Cross-app checks*"]
        for cross in receipt.crosschecks:
            mark = ":white_check_mark: PASS" if cross.passed else ":x: FAIL"
            lines.append(f"{mark} `{cross.name}` (reads {cross.reads_from})")
            lines.append(f">{cross.detail[:280]}")

    if receipt.manual_remediation:
        lines += ["", ":rotating_light: *Needs a human*"]
        for item in receipt.manual_remediation:
            lines.append(f"• `{item.app}.{item.action}` → `{item.object_id}`")
            lines.append(f">{item.what[:240]}")

    return "\n".join(lines)


# -- Socket Mode transport ---------------------------------------------------


def _live_order_resolver():
    """READ-ONLY enumeration of refundable PaymentIntents since a timestamp.

    Lists rather than searches: Stripe's search index lags writes, and an
    enumeration that silently omits a recent order would understate the blast
    radius of a bulk refund -- the one number a human is being asked to judge.

    Results are memoised per window for the life of one request so the plan
    post and the runner's own re-plan do not both pay for the scan.
    """
    import stripe as stripe_sdk

    cache: dict[str, list[dict]] = {}

    def resolve(since: datetime) -> list[dict]:
        key = since.isoformat()
        if key in cache:
            return cache[key]

        stripe_sdk.api_key = os.environ["STRIPE_SECRET_KEY"]
        found: list[dict] = []
        scanned = 0
        for intent in stripe_sdk.PaymentIntent.list(
            limit=100, created={"gte": int(since.timestamp())}
        ).auto_paging_iter():
            scanned += 1
            if scanned > 500:
                break
            if intent.status != "succeeded":
                continue
            meta = intent.metadata.to_dict() if hasattr(intent.metadata, "to_dict") else {}
            order_id = meta.get("order_id")
            if not order_id:
                continue
            refunded = sum(
                int(r.amount)
                for r in stripe_sdk.Refund.list(payment_intent=intent.id, limit=100).data
                if r.status == "succeeded"
            )
            if refunded:
                continue  # already refunded; nothing left to refund
            found.append({
                "order_id": str(order_id),
                "amount_cents": int(intent.amount_received or intent.amount),
                "created": intent.created,
            })
        cache[key] = found
        return found

    return resolve


def main() -> int:
    from dotenv import load_dotenv
    from slack_sdk import WebClient
    from slack_sdk.socket_mode.builtin.client import SocketModeClient
    from slack_sdk.socket_mode.response import SocketModeResponse

    load_dotenv()
    missing = [
        key for key in ("SLACK_APP_TOKEN", "SLACK_BOT_TOKEN", "SLACK_CHANNEL_ID")
        if not os.environ.get(key)
    ]
    if missing:
        print(f"ERROR: missing env var(s): {', '.join(missing)}")
        return 2

    web = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    identity = web.auth_test()
    app = SlackApp(
        client=web,
        channel=os.environ["SLACK_CHANNEL_ID"],
        bot_user_id=identity["user_id"],
        order_resolver=_live_order_resolver(),
    )

    socket = SocketModeClient(
        app_token=os.environ["SLACK_APP_TOKEN"], web_client=web
    )

    def on_request(client: SocketModeClient, req) -> None:
        # Ack first, always. Slack retries anything unacked within 3s, and a
        # retry here would be a second run of the same request.
        client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))

        try:
            if req.type == "events_api":
                event = (req.payload or {}).get("event", {}) or {}
                if event.get("type") in ("message", "app_mention"):
                    app.handle_envelope(req.payload or {})
                return

            if req.type == "interactive":
                payload = req.payload or {}
                for action in payload.get("actions", []) or []:
                    action_id = action.get("action_id")
                    if action_id not in (ACTION_APPROVE, ACTION_CANCEL, ACTION_CONFIRM):
                        continue
                    app.handle_decision(
                        "cancel" if action_id == ACTION_CANCEL else "approve",
                        action.get("value", ""),
                        user=(payload.get("user") or {}).get("id", "someone"),
                    )
        except Exception as exc:  # noqa: BLE001 - never kill the listener
            # Deliberately no payload dump: Slack envelopes carry tokens.
            print(f"handler error: {type(exc).__name__}: {exc}")

    socket.socket_mode_request_listeners.append(on_request)
    socket.connect()

    print(
        f"Readback is listening as @{identity['user']} "
        f"in channel {os.environ['SLACK_CHANNEL_ID']} "
        f"({identity['team']}). Trigger with an @mention or 'readback: <request>'."
    )
    threading.Event().wait()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
