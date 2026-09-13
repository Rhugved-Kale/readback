"""Slack adapter. Interface only — no implementation yet."""

from __future__ import annotations

from ..types import Effect, EffectResult
from .base import Adapter


class SlackAdapter(Adapter):
    name = "slack"

    def __init__(self, client=None, channel_id: str | None = None, **kwargs) -> None:
        # TODO: accept a slack_sdk.WebClient; read SLACK_BOT_TOKEN and
        #       SLACK_CHANNEL_ID from the environment.
        self.client = client
        self.channel_id = channel_id

    def plan(self, request) -> list[Effect]:
        # TODO: no API call. Render the message text for the request and emit a
        #       single post_message effect carrying channel + text.
        raise NotImplementedError

    def apply(self, effect: Effect) -> EffectResult:
        # TODO: post_message -> client.chat_postMessage(
        #           channel=effect.params["channel"],
        #           text=effect.params["text"],
        #           metadata={"event_type": "readback_effect",
        #                     "event_payload": {"key": effect.idempotency_key}})
        #       Slack has no idempotency key, so the metadata payload is what
        #       makes the write findable on read-back and safe to retry.
        raise NotImplementedError

    def verify(self, effect: Effect) -> tuple[bool, str]:
        # TODO: post_message -> client.conversations_history(
        #           channel=effect.params["channel"], limit=50) as a FRESH call;
        #       scan for EXACTLY ONE message whose metadata event_payload.key
        #       equals effect.idempotency_key, and assert its text matches.
        #       Two matches means a retry double-posted and must fail the run.
        #       Do NOT trust the `ts` returned by apply().
        raise NotImplementedError

    def compensate(self, effect: Effect) -> EffectResult:
        # TODO: post_message -> client.chat_delete(channel=..., ts=...) where ts
        #       is re-discovered via conversations_history, not taken from
        #       apply(). If chat_delete fails (message too old, or the token
        #       lacks chat:write for another author), fall back to
        #       chat_postMessage with a retraction in the same thread and say so
        #       in the EffectResult rather than claiming a clean rollback.
        raise NotImplementedError
