"""The adapter contract every provider integration must satisfy."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..types import Effect, EffectResult


class Adapter(ABC):
    """One provider (Stripe, Notion, Slack) behind four required methods.

    The contract is deliberately small and deliberately paranoid. Its single
    organizing rule:

        **A write is not believed because the provider said so.
        A write is believed because a later, independent read found it.**

    Everything below follows from that rule.
    """

    #: Short provider name used in effects, the WAL, and receipts.
    name: str

    @abstractmethod
    def plan(self, request) -> list[Effect]:
        """Translate a request into this provider's share of the work.

        Returns an ordered list of Effects this adapter would apply. Planning is
        pure: it must not write, and it must not depend on state it has not
        read. If the request is not actionable for this provider, return [].

        Every returned Effect must carry a stable `idempotency_key`. The key is
        what makes crash recovery safe, so it must be derived from the *logical*
        write (e.g. the order ID being refunded), never from a timestamp, a
        random value, or anything else that changes between attempts.
        """

    @abstractmethod
    def apply(self, effect: Effect) -> EffectResult:
        """Commit one Effect against the provider.

        Must send `effect.idempotency_key` to the provider wherever the provider
        supports it, so that a retry after a crash or timeout is absorbed
        upstream rather than duplicating the write.

        The returned EffectResult is a *report*, not a verdict:

        - `status == "ok"` does NOT mean the write is durable. Only verify()
          can establish that.
        - `status == "failed"` does NOT mean the write did not land. A 500 or a
          timeout frequently follows a write that committed. The runner
          therefore verifies failed effects too, and promotes them to COMMITTED
          when read-back finds them.

        Raising is reserved for genuinely unexpected conditions (a crash). An
        expected provider error should come back as a failed EffectResult with
        `error` populated.
        """

    @abstractmethod
    def verify(self, effect: Effect) -> tuple[bool, str]:
        """Re-read LIVE provider state and assert the Effect actually landed.

        Returns (passed, detail), where `detail` is a human-readable sentence
        naming what was expected and what was actually found. `detail` is
        surfaced verbatim in the receipt, so write it for a reader who is
        deciding whether to trust the run.

        Hard requirements:

        1. **Issue a new request to the provider.** A fresh GET/query/history
           call, every time. No cached client state, no memoized value.
        2. **Never read apply()'s return value.** verify() does not receive the
           EffectResult and must not reach for one. The provider's response to
           the write is exactly the thing under suspicion; using it here would
           make read-back a tautology and defeat the entire design.
        3. **Assert the post-state, not the operation.** Check that the refund
           exists and the amount matches — not that some call returned 200.
        4. **Be replica-lag aware.** A single read that disagrees may be stale
           rather than wrong. Re-read within a bounded budget before failing.
        """

    @abstractmethod
    def compensate(self, effect: Effect) -> EffectResult:
        """Reverse an already-committed Effect.

        Called only during rollback, only for effects the WAL records as
        COMMITTED, and only in reverse commit order.

        Must be idempotent and must tolerate a world where the original write is
        already gone: compensating a reversal that already happened is a no-op
        returning `status == "skipped"`, not an error.

        Where a provider has no true inverse (a Slack message cannot be unsent
        after the edit window; a refund cannot be un-refunded), the compensation
        is the closest honest thing — delete the message, post a correction, add
        a Notion row recording the reversal — and the EffectResult must say in
        `provider_response` what was actually done, so the receipt does not
        overstate the rollback.
        """
