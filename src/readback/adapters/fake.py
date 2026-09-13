"""An in-memory Adapter used by the eval harness and the unit tests.

FakeAdapter is a real implementation of the full contract, not a stub. It keeps
a dict of records, applies writes into it, and verifies by reading back out of
it through a separate code path that never touches apply()'s return value.

It also injects the faults that make read-back worth having: writes that land
and then report 500, writes that commit and then time out, rate-limit storms,
and stale reads. All faults are off by default.
"""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from typing import Any

from ..types import STATUS_FAILED, STATUS_OK, STATUS_SKIPPED, Effect, EffectResult
from .base import Adapter

#: How many fresh reads verify() will spend waiting for a replica to catch up.
READ_RETRY_BUDGET = 4

#: How many times apply() retries its own 429s before giving up.
APPLY_RETRY_BUDGET = 5


@dataclass
class FaultConfig:
    """Faults to inject. Every field defaults to "no fault"."""

    #: Write lands in the store, then apply() reports HTTP 500.
    fail_after_write: bool = False

    #: Write lands in the store, then the client raises a read timeout.
    timeout_after_commit: bool = False

    #: Return HTTP 429 for the first N apply attempts, then succeed.
    rate_limit_storm: int = 0

    #: Serve pre-write state for the first N verify reads.
    stale_read: int = 0

    def any_enabled(self) -> bool:
        return bool(
            self.fail_after_write
            or self.timeout_after_commit
            or self.rate_limit_storm
            or self.stale_read
        )


@dataclass
class FakeAdapter(Adapter):
    """In-memory provider. `name` is the app key used in Effects and the WAL."""

    name: str
    faults: FaultConfig = field(default_factory=FaultConfig)

    #: Live state, keyed by idempotency_key.
    store: dict[str, dict[str, Any]] = field(default_factory=dict)

    #: Number of times a record was actually mutated, keyed by idempotency_key.
    #: A value above 1 is a double-write and a bug.
    write_count: dict[str, int] = field(default_factory=dict)

    #: Every provider round trip, for assertions and for the receipt.
    call_log: list[dict[str, Any]] = field(default_factory=list)

    _rate_limit_remaining: int = field(default=0, init=False)
    _stale_remaining: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self._rate_limit_remaining = self.faults.rate_limit_storm
        self._stale_remaining = self.faults.stale_read

    # -- contract ---------------------------------------------------------

    def plan(self, request) -> list[Effect]:
        """Return this provider's share of the planned effects.

        Delegates to the shared planner and filters by app, so the fake plans
        exactly what the real adapters will plan.
        """
        from ..planner import plan_request

        result = plan_request(str(request))
        return [e for e in result.effects if e.app == self.name]

    def apply(self, effect: Effect) -> EffectResult:
        """Write into the store, honouring the idempotency key and any faults."""
        started = time.perf_counter()

        # Rate-limit storm: the provider rejects us before the write is even
        # attempted. We retry in-process; because the write is keyed by the
        # idempotency key, retrying cannot duplicate it.
        attempts = 0
        while self._rate_limit_remaining > 0 and attempts < APPLY_RETRY_BUDGET:
            self._rate_limit_remaining -= 1
            attempts += 1
            self._log("apply", effect, "429 rate_limited")
        if self._rate_limit_remaining > 0:
            return self._result(
                effect, STATUS_FAILED, started, error="429 rate_limited: retry budget exhausted"
            )

        self._write(effect)
        self._log("apply", effect, "write committed")

        if self.faults.fail_after_write:
            # The write is in the store. The provider still reports a 500.
            return self._result(
                effect,
                STATUS_FAILED,
                started,
                error="500 internal_server_error (write may have landed)",
            )

        if self.faults.timeout_after_commit:
            # The write is in the store. We never saw the response.
            return self._result(
                effect,
                STATUS_FAILED,
                started,
                error="read timeout after commit (write may have landed)",
            )

        return self._result(
            effect,
            STATUS_OK,
            started,
            provider_response={"id": self._provider_id(effect), "retries": attempts},
        )

    def verify(self, effect: Effect) -> tuple[bool, str]:
        """Re-read live state and assert the effect is present and correct.

        Note what this does NOT do: it never looks at an EffectResult. It knows
        only the Effect (what was *intended*) and whatever a fresh read returns.
        """
        detail = ""
        for attempt in range(READ_RETRY_BUDGET):
            record = self._read(effect.idempotency_key)
            if record is None:
                detail = (
                    f"{self.name}.{effect.action}: expected a record for "
                    f"{effect.idempotency_key!r}, live read found none"
                )
                continue

            mismatches = [
                f"{key}: expected {value!r}, live value {record.get(key)!r}"
                for key, value in effect.params.items()
                if record.get(key) != value
            ]
            if not mismatches:
                return True, (
                    f"{self.name}.{effect.action}: live read confirms "
                    f"{self._describe(effect)} (read attempt {attempt + 1})"
                )
            detail = f"{self.name}.{effect.action}: " + "; ".join(mismatches)

        return False, detail

    def compensate(self, effect: Effect) -> EffectResult:
        """Remove the record this effect created. A no-op if it is already gone."""
        started = time.perf_counter()
        if effect.idempotency_key not in self.store:
            self._log("compensate", effect, "already absent, no-op")
            return self._result(
                effect,
                STATUS_SKIPPED,
                started,
                provider_response={"note": "nothing to reverse; record already absent"},
            )

        removed = self.store.pop(effect.idempotency_key)
        self._log("compensate", effect, "record reversed")
        return self._result(
            effect,
            STATUS_OK,
            started,
            provider_response={"reversed": removed},
        )

    # -- test / harness helpers -------------------------------------------

    def drift(self, idempotency_key: str, **changes: Any) -> None:
        """Mutate live state behind the runner's back.

        Simulates the case read-back exists to catch: the write reported
        success, and then live state does not say what we think it says.
        Passing no changes deletes the record outright.
        """
        if not changes:
            self.store.pop(idempotency_key, None)
            return
        self.store.setdefault(idempotency_key, {}).update(changes)

    def snapshot(self) -> dict[str, dict[str, Any]]:
        """Deep copy of live state, used for the receipt's state diff."""
        return copy.deepcopy(self.store)

    # -- internals ---------------------------------------------------------

    def _write(self, effect: Effect) -> None:
        """Idempotent store write: the same key never counts twice."""
        if effect.idempotency_key in self.store:
            # The provider absorbed the duplicate. Do not bump write_count.
            return
        self.store[effect.idempotency_key] = dict(effect.params)
        self.write_count[effect.idempotency_key] = (
            self.write_count.get(effect.idempotency_key, 0) + 1
        )

    def _read(self, idempotency_key: str) -> dict[str, Any] | None:
        """A fresh provider read. Serves stale state while the fault is armed."""
        self.call_log.append({"op": "read", "key": idempotency_key, "app": self.name})
        if self._stale_remaining > 0:
            self._stale_remaining -= 1
            return None  # pre-write state
        record = self.store.get(idempotency_key)
        return dict(record) if record is not None else None

    def _provider_id(self, effect: Effect) -> str:
        return f"{self.name}_{effect.action}_{abs(hash(effect.idempotency_key)) % 10**8:08d}"

    def _describe(self, effect: Effect) -> str:
        if not effect.params:
            return "the record exists"
        return ", ".join(f"{k}={v!r}" for k, v in effect.params.items())

    def _log(self, op: str, effect: Effect, note: str) -> None:
        self.call_log.append(
            {"op": op, "app": self.name, "action": effect.action,
             "key": effect.idempotency_key, "note": note}
        )

    def _result(
        self,
        effect: Effect,
        status: str,
        started: float,
        provider_response: Any = None,
        error: str | None = None,
    ) -> EffectResult:
        return EffectResult(
            effect_id=effect.id,
            status=status,
            provider_response=provider_response,
            latency_ms=(time.perf_counter() - started) * 1000.0,
            error=error,
        )
