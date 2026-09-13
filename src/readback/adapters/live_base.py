"""Shared machinery for the three live adapters.

Holds only what all three genuinely need: action-name resolution, EffectResult
construction from a retry Outcome, and the bounded re-read loop that verify()
uses to distinguish replica lag from a genuinely missing write.
"""

from __future__ import annotations

import os
import time
from typing import Any, Callable

from ..core import retry
from ..types import STATUS_FAILED, STATUS_OK, STATUS_SKIPPED, Effect, EffectResult

#: How verify() tolerates read-your-writes lag. A single disagreeing read is
#: not proof of absence; N disagreeing reads across a bounded window is. Kept
#: small because a slow verify delays compensation, which is the expensive path.
VERIFY_ATTEMPTS = 3
VERIFY_DELAY_S = 0.6


class LiveAdapter:
    """Common base for StripeAdapter, NotionAdapter, SlackAdapter."""

    name: str = ""

    #: Canonical action -> handler suffix. Subclasses fill this in.
    ACTIONS: dict[str, str] = {}

    #: The planner predates this spec and emits the older action names. Rather
    #: than rewrite the planner (and with it the fake-adapter tests that pin its
    #: output), the older name is accepted as an alias of the canonical one.
    #: Canonical names are what the adapters, receipts and cross-checks use.
    ALIASES: dict[str, str] = {
        "create_price": "update_price",
        "update_catalog_row": "update_catalog_price",
    }

    def canonical(self, action: str) -> str:
        return self.ALIASES.get(action, action)

    # -- result helpers ----------------------------------------------------

    def _ok(
        self,
        effect: Effect,
        outcome: retry.Outcome,
        response: Any = None,
        status: str = STATUS_OK,
    ) -> EffectResult:
        """Build a success/skip EffectResult carrying the full attempt history.

        `provider_response["attempts"]` is the per-attempt record the receipt
        renders, so a call that succeeded only on its third try is visible as
        such instead of being flattened into one latency number.
        """
        body: dict[str, Any] = {"attempts": [a.to_dict() for a in outcome.attempts]}
        if response is not None:
            body.update(response if isinstance(response, dict) else {"value": response})
        return EffectResult(
            effect_id=effect.id,
            status=status,
            provider_response=body,
            latency_ms=outcome.total_latency_ms,
        )

    def _failed(self, effect: Effect, outcome: retry.Outcome, note: str = "") -> EffectResult:
        """Build a failed EffectResult.

        Deliberately NOT a verdict that the write is absent — a 500 after a
        committed write looks exactly like this. The runner still verifies it.
        """
        return EffectResult(
            effect_id=effect.id,
            status=STATUS_FAILED,
            provider_response={"attempts": [a.to_dict() for a in outcome.attempts]},
            latency_ms=outcome.total_latency_ms,
            error=f"{note + ': ' if note else ''}{outcome.error}",
        )

    def _skipped(self, effect: Effect, note: str, response: Any = None) -> EffectResult:
        return EffectResult(
            effect_id=effect.id,
            status=STATUS_SKIPPED,
            provider_response={"note": note, **(response or {})},
            latency_ms=0.0,
        )

    # -- verify helper -----------------------------------------------------

    def _reread(
        self,
        check: Callable[[int], tuple[bool, str]],
        attempts: int = VERIFY_ATTEMPTS,
        delay: float = VERIFY_DELAY_S,
        sleep: Callable[[float], None] = time.sleep,
    ) -> tuple[bool, str]:
        """Run a live read up to `attempts` times, stopping at the first pass.

        `check(attempt_number)` must issue a FRESH provider request every call.
        Each invocation is a new round trip; nothing is memoized between them,
        which is what makes the retry a lag tolerance rather than a cache hit.
        """
        last = (False, "verify never ran")
        for number in range(1, attempts + 1):
            try:
                passed, detail = check(number)
            except BaseException as exc:  # noqa: BLE001
                passed, detail = False, f"read failed: {type(exc).__name__}: {exc}"
            last = (passed, detail)
            if passed:
                return passed, detail
            if number < attempts:
                sleep(delay)
        return last


def env(key: str, default: str = "") -> str:
    value = os.environ.get(key, default)
    if not value:
        raise RuntimeError(
            f"{key} is not set. Live adapters need real credentials; "
            f"copy .env.example to .env and fill it in."
        )
    return value
