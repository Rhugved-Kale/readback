"""Slack adapter against the live API.

    slack.post_message(text)

IDEMPOTENCY LIMITATION: chat.postMessage has no idempotency key. Posting the
same text twice produces two messages. The defences mirror Notion's:
  1. the WAL's already_committed() check;
  2. a pre-write scan of recent channel history for a message already carrying
     this run marker (below);
  3. verify(), which matches on the exact marker so a duplicate is visible.

Every message carries a trailing `[readback run <run_id>]` marker. That marker
is what makes defence 2 and 3 possible at all -- without it there is no way to
tell our own post from an identical one a human made. It is also why verify()
can reconstruct the expected text deterministically from the Effect alone,
instead of reading what apply() returned.
"""

from __future__ import annotations

import os
from typing import Any

from slack_sdk import WebClient

from ..core import retry
from ..types import Effect, EffectResult, IrreversibleEffect
from .base import Adapter
from .live_base import LiveAdapter

#: How far back to scan history for the dedupe check and for verify().
HISTORY_LIMIT = 200


class SlackAdapter(LiveAdapter, Adapter):
    name = "slack"

    ACTIONS = {"post_message": "post"}

    def __init__(self, client=None, run_id: str = "", channel: str | None = None) -> None:
        self.client = client or WebClient(token=os.environ.get("SLACK_BOT_TOKEN", ""))
        self.run_id = run_id
        self.channel = channel or os.environ.get("SLACK_CHANNEL_ID", "")

    # -- plan --------------------------------------------------------------

    def plan(self, request) -> list[Effect]:
        """Slack's share of a request. Pure: no writes, no reads."""
        return [
            e for e in (getattr(request, "effects", request) or [])
            if isinstance(e, Effect) and e.app == self.name
        ]

    # -- apply -------------------------------------------------------------

    def apply(self, effect: Effect) -> EffectResult:
        if self.canonical(effect.action) != "post_message":
            return self._skipped(effect, f"slack adapter does not handle {effect.action!r}")

        channel = self._channel(effect)
        text = self._expected_text(effect)

        # Pre-write state: posting is an INSERT, so "no message existed" is the
        # state compensate() restores by deleting what we post.
        effect.reversible = True
        effect.prior_state = {"existed_before": False, "channel": channel, "ts": None}

        # Defence 2: don't post twice for the same run.
        existing = self._find_by_marker(channel, effect)
        if existing:
            effect.prior_state["ts"] = existing["ts"]
            return self._skipped(
                effect,
                f"message for run {self._run_id(effect)} already in channel; not reposting",
                {"ts": existing["ts"], "channel": channel},
            )

        outcome = retry.call(
            lambda: self.client.chat_postMessage(channel=channel, text=text),
            op="chat.postMessage",
        )
        if not outcome.ok:
            return self._failed(effect, outcome, "chat.postMessage")

        ts = outcome.value["ts"]
        effect.prior_state["ts"] = ts
        return self._ok(effect, outcome, {"ts": ts, "channel": channel})

    # -- verify ------------------------------------------------------------

    def verify(self, effect: Effect) -> tuple[bool, str]:
        """Re-read live Slack state.

        HARD RULE: this issues a FRESH conversations.history call every time and
        never reads the postMessage response. The `ts` it looks for comes from
        the WAL-persisted prior_state when available, but the message is located
        and its text compared by scanning live history -- and when no ts is
        available at all (bare replay) it falls back to matching the run marker,
        so the verdict is reachable from the Effect alone.
        """
        if self.canonical(effect.action) != "post_message":
            return False, f"slack adapter cannot verify {effect.action!r}"

        channel = self._channel(effect)
        expected_text = self._expected_text(effect)
        want_ts = (effect.prior_state or {}).get("ts")

        def check(attempt: int) -> tuple[bool, str]:
            # FRESH history read on every attempt.
            messages = self._history(channel)
            if want_ts:
                match = next((m for m in messages if m.get("ts") == want_ts), None)
                located = f"ts={want_ts}"
            else:
                marker = self._marker(effect)
                hits = [m for m in messages if marker in (m.get("text") or "")]
                match = hits[0] if hits else None
                located = f"marker {marker!r}"
                if len(hits) > 1:
                    return False, (
                        f"slack.post_message: expected exactly 1 message carrying "
                        f"{marker!r}, live history shows {len(hits)} -- a duplicate post "
                        f"landed (read attempt {attempt})"
                    )

            if match is None:
                return False, (
                    f"slack.post_message: no message matching {located} in the last "
                    f"{HISTORY_LIMIT} messages of {channel} (read attempt {attempt})"
                )

            actual = match.get("text") or ""
            if actual.strip() != expected_text.strip():
                return False, (
                    f"slack.post_message: message {match.get('ts')} text mismatch. "
                    f"expected {expected_text!r}, live Slack reports {actual!r} "
                    f"(read attempt {attempt})"
                )
            return True, (
                f"slack.post_message: live history read confirms message "
                f"{match.get('ts')} in {channel} with matching text "
                f"(read attempt {attempt})"
            )

        return self._reread(check)

    # -- compensate --------------------------------------------------------

    def compensate(self, effect: Effect) -> EffectResult:
        """Delete the message this effect posted.

        chat.delete is a true inverse only while the bot still owns the message
        and the workspace allows deletion. When it does not, the honest answer
        is an IrreversibleEffect naming the ts, not a silent pass.
        """
        if self.canonical(effect.action) != "post_message":
            return self._skipped(effect, f"nothing to compensate for {effect.action!r}")

        prior = effect.prior_state or {}
        channel = prior.get("channel") or self._channel(effect)
        ts = prior.get("ts")

        if not ts:
            # Locate it fresh rather than leaving a stray post behind.
            found = self._find_by_marker(channel, effect)
            ts = found["ts"] if found else None
        if not ts:
            return self._skipped(effect, "no message found to delete")

        # Already gone is a no-op, not an error (Adapter contract).
        if not any(m.get("ts") == ts for m in self._history(channel)):
            return self._skipped(effect, "message already deleted", {"ts": ts})

        outcome = retry.call(
            lambda: self.client.chat_delete(channel=channel, ts=ts), op="chat.delete"
        )
        if not outcome.ok:
            raise IrreversibleEffect(
                f"Slack message {ts} in {channel} could not be deleted: {outcome.error}. "
                f"The post is still visible to everyone in the channel.",
                app=self.name,
                object_id=str(ts),
            )
        return self._ok(effect, outcome, {
            "deleted_ts": ts,
            "channel": channel,
            "note": "message deleted from the channel",
        })

    def post_notice(self, text: str) -> str | None:
        """Post an out-of-band operational notice, outside the Effect machinery.

        Used by the runner to announce PARTIAL_MANUAL_REMEDIATION. Deliberately
        not an Effect: it is not part of the plan, must not be compensated, and
        must still go out when the run as a whole has failed. Returns the ts, or
        None if the post failed -- the caller treats this as best effort because
        the receipt on disk is the durable record.
        """
        outcome = retry.call(
            lambda: self.client.chat_postMessage(channel=self.channel, text=text),
            op="chat.postMessage(notice)",
        )
        return outcome.value["ts"] if outcome.ok else None

    # -- live reads used by cross-checks -----------------------------------

    def live_message(self, effect: Effect) -> dict[str, Any] | None:
        """Fresh read of this run's message. Used by crosscheck.py."""
        return self._find_by_marker(self._channel(effect), effect)

    # -- internals ---------------------------------------------------------

    def _history(self, channel: str) -> list[dict]:
        return self.client.conversations_history(
            channel=channel, limit=HISTORY_LIMIT
        ).get("messages", [])

    def _find_by_marker(self, channel: str, effect: Effect) -> dict | None:
        marker = self._marker(effect)
        for message in self._history(channel):
            if marker in (message.get("text") or ""):
                return message
        return None

    def _channel(self, effect: Effect) -> str:
        """Resolve the target channel.

        The planner emits the literal placeholder 'SLACK_CHANNEL_ID', which
        means "whatever the environment points at" rather than a channel named
        that. Anything else is taken as a real channel id.
        """
        value = str(effect.params.get("channel") or "")
        if not value or value == "SLACK_CHANNEL_ID":
            return self.channel
        return value

    def _run_id(self, effect: Effect) -> str:
        return str(effect.params.get("run_id") or self.run_id or "")

    def _marker(self, effect: Effect) -> str:
        return f"[readback run {self._run_id(effect)}]"

    def _expected_text(self, effect: Effect) -> str:
        """The exact text this effect posts, derived only from the Effect.

        Deterministic on purpose: verify() recomputes it rather than comparing
        against whatever apply() sent, so a restarted process checks the same
        string this one posted.
        """
        body = str(effect.params.get("text") or "")
        return f"{body}\n{self._marker(effect)}"
