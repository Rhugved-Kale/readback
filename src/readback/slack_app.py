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
from dataclasses import dataclass, field
from typing import Any, Callable

from .core.receipt import (
    OUTCOME_FAILURE,
    OUTCOME_HELD,
    OUTCOME_PARTIAL,
    OUTCOME_REFUSED,
    OUTCOME_SUCCESS,
    Receipt,
)
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


@dataclass
class HeldRun:
    """A plan the risk gate stopped, waiting on a human."""

    run_id: str
    request: str
    channel: str
    thread_ts: str
    gate_reason: str
    requester: str


@dataclass
class SlackApp:
    """Request handling, independent of the Socket Mode transport."""

    client: Any
    channel: str
    bot_user_id: str = ""
    runner: Callable[..., Receipt] = run_request
    root: str = "runs"

    #: One run at a time. Ops writes against three live systems should never
    #: interleave: two concurrent repricings would each verify a world the
    #: other is still changing, and rollback order would be undefined.
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _in_flight: str | None = field(default=None, init=False)
    _held: dict[str, HeldRun] = field(default_factory=dict, init=False)

    # -- entry points ------------------------------------------------------

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
            plan = plan_request(request)

            if plan.refused or not plan.effects:
                reason = plan.refusal or "The planner produced no effects for this request."
                self._post(thread_ts, f"*Refused* — run `{run_id}`\n>{reason}")
                return "refused:planner"

            self._post(thread_ts, _plan_message(run_id, request, plan.effects))

            gate = riskgate.evaluate(request, plan.effects)
            if gate.held:
                self._held[run_id] = HeldRun(
                    run_id=run_id, request=request, channel=self.channel,
                    thread_ts=thread_ts, gate_reason=gate.reason, requester=user,
                )
                self._post_blocks(
                    thread_ts,
                    text=f"Held for approval — run {run_id}",
                    blocks=_hold_blocks(run_id, gate.reason, plan.effects),
                )
                return "held"

            receipt = self.runner(
                request, adapters=self._adapters(run_id), run_id=run_id, root=self.root
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
            )
            self._post(held.thread_ts, _receipt_message(receipt))
            return f"approved:{receipt.outcome}"
        finally:
            with self._lock:
                if self._in_flight == run_id:
                    self._in_flight = None

    # -- helpers -----------------------------------------------------------

    def _adapters(self, run_id: str) -> dict[str, Any]:
        from .adapters.live import build_live_adapters

        return build_live_adapters(run_id)

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


def _plan_message(run_id: str, request: str, effects: list) -> str:
    lines = [f"*Plan for run* `{run_id}`", f">{request}", ""]
    for index, effect in enumerate(effects, 1):
        lines.append(f"{index}. `{effect.app}` · *{effect.action}*")
    return "\n".join(lines)


def _hold_blocks(run_id: str, gate_reason: str, effects: list) -> list:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f":warning: *Held by the risk gate* — run `{run_id}`\n"
                    f"*Rule:* {gate_reason}\n"
                    f"*Plan:* {len(effects)} effect(s). Nothing has been applied."
                ),
            },
        },
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


def _receipt_message(receipt: Receipt) -> str:
    lines = [
        f"{_OUTCOME_HEADER.get(receipt.outcome, receipt.outcome.upper())} — run `{receipt.run_id}`",
        f">{receipt.reason}",
    ]

    if receipt.approval:
        lines.append(
            f">_Released by {receipt.approval['approver']} despite: "
            f"{receipt.approval.get('gate_reason', '')}_"
        )

    if receipt.calls:
        lines += ["", "*Provider calls*", "```"]
        for call in receipt.calls:
            lines.append(
                f"{call.status:<13} {call.phase:<11} {call.app}.{call.action:<22} "
                f"{call.latency_ms:8.1f}ms"
            )
            if call.error:
                lines.append(f"              error: {call.error[:110]}")
        lines.append("```")

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
                    app.handle_message(event)
                return

            if req.type == "interactive":
                payload = req.payload or {}
                for action in payload.get("actions", []) or []:
                    action_id = action.get("action_id")
                    if action_id not in (ACTION_APPROVE, ACTION_CANCEL):
                        continue
                    app.handle_decision(
                        "approve" if action_id == ACTION_APPROVE else "cancel",
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
