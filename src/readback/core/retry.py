"""One retry policy, shared by every adapter.

Retries are a correctness hazard in this system, not a convenience. A retried
write can land twice, so the rules are deliberately narrow:

* **Retry only 429 and 5xx.** These are the two cases where the request may not
  have been processed, or where the provider is explicitly asking us to wait.
* **Never retry 4xx.** A 400/403/404 is a statement about the request itself.
  Sending it again produces the same answer and hides the real error.
* **Every attempt is recorded separately.** A call that succeeded on attempt 3
  after two 429s is not the same operational fact as one that succeeded first
  try, and the receipt has to show the difference.

A retried write that DID land is not this module's problem to solve: it is
absorbed by the provider's idempotency key where one exists (Stripe), and
caught by read-back everywhere else. Retry never decides whether a write is
durable — only verify() does.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable

#: Retry tuning. One block, so the policy is auditable at a glance.
MAX_ATTEMPTS = 3
BASE_DELAY_S = 0.5          # first backoff, doubled per attempt
MAX_DELAY_S = 8.0           # ceiling before jitter
JITTER = 0.5                # full-jitter fraction: delay *= (1 - J*random())

#: The only statuses that may be retried.
RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})

#: Exception type *names* that mean "never reached the provider". Matched by
#: name so this module imports no SDK and stays usable without credentials.
RETRYABLE_EXC_NAMES = frozenset({
    "APIConnectionError",      # stripe
    "RequestTimeoutError",     # notion_client
    "ConnectionError",
    "Timeout",
    "TimeoutError",
    "ReadTimeout",
    "ConnectTimeout",
})


@dataclass
class Attempt:
    """One physical round trip to a provider."""

    number: int
    status: str                     # ok | retrying | failed
    latency_ms: float
    http_status: int | None = None
    error: str | None = None
    slept_ms: float = 0.0
    #: Which provider call this was. One Effect can span several distinct calls
    #: (create price, promote to default, archive old); without this label the
    #: receipt shows three separate "attempt 1" lines and reads like a retry
    #: loop that never advanced.
    op: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "attempt": self.number,
            "op": self.op,
            "status": self.status,
            "latency_ms": round(self.latency_ms, 2),
            "http_status": self.http_status,
            "error": self.error,
            "slept_ms": round(self.slept_ms, 2),
        }


@dataclass
class Outcome:
    """The result of a retried call, with the full attempt history."""

    ok: bool
    value: Any = None
    error: str | None = None
    http_status: int | None = None
    attempts: list[Attempt] = field(default_factory=list)

    @property
    def total_latency_ms(self) -> float:
        """Wall time actually spent talking to the provider, excluding sleeps."""
        return sum(a.latency_ms for a in self.attempts)

    @property
    def summary(self) -> str:
        if len(self.attempts) == 1:
            return "1 attempt"
        return f"{len(self.attempts)} attempts"

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "error": self.error,
            "http_status": self.http_status,
            "attempts": [a.to_dict() for a in self.attempts],
            "total_latency_ms": round(self.total_latency_ms, 2),
        }


def http_status_of(exc: BaseException) -> int | None:
    """Best-effort HTTP status from any of the three SDKs' error types.

    Duck-typed rather than isinstance-checked so this module imports no SDK:
      stripe        -> exc.http_status
      notion_client -> exc.status
      slack_sdk     -> exc.response.status_code
    """
    for attr in ("http_status", "status_code", "status"):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value

    response = getattr(exc, "response", None)
    if response is not None:
        code = getattr(response, "status_code", None)
        if isinstance(code, int):
            return code
        # slack_sdk SlackApiError: rate limits surface as an error *string*
        # with the HTTP status already unwrapped by the SDK.
        try:
            if response.get("error") == "ratelimited":
                return 429
        except Exception:
            pass
    return None


def is_retryable(exc: BaseException) -> bool:
    """True only for 429, 5xx, and errors that never reached the provider."""
    status = http_status_of(exc)
    if status is not None:
        return status in RETRYABLE_STATUSES
    return type(exc).__name__ in RETRYABLE_EXC_NAMES


def backoff_delay(attempt_number: int, rng: random.Random | None = None) -> float:
    """Exponential backoff with full jitter.

    Jitter matters more than the exponent here: without it, N effects that all
    hit the same 429 retry in lockstep and reproduce the storm they are backing
    off from.
    """
    rng = rng or random
    raw = min(BASE_DELAY_S * (2 ** (attempt_number - 1)), MAX_DELAY_S)
    return raw * (1.0 - JITTER * rng.random())


def merge(*outcomes: "Outcome") -> "Outcome":
    """Combine the histories of several calls made for ONE effect.

    Attempts are renumbered sequentially across the whole effect, so a receipt
    reads 1,2,3 for three distinct provider calls rather than three separate
    attempt-1 lines that look like a stalled retry.
    """
    merged: list[Attempt] = []
    for outcome in outcomes:
        if outcome is None:
            continue
        for attempt in outcome.attempts:
            merged.append(
                Attempt(
                    number=len(merged) + 1,
                    status=attempt.status,
                    latency_ms=attempt.latency_ms,
                    http_status=attempt.http_status,
                    error=attempt.error,
                    slept_ms=attempt.slept_ms,
                    op=attempt.op,
                )
            )
    return Outcome(ok=all(o.ok for o in outcomes if o is not None), attempts=merged)


def call(
    fn: Callable[[], Any],
    *,
    op: str = "",
    max_attempts: int = MAX_ATTEMPTS,
    sleep: Callable[[float], None] = time.sleep,
    rng: random.Random | None = None,
) -> Outcome:
    """Invoke `fn` with the shared retry policy and return an Outcome.

    Never raises for provider errors — the failure comes back as
    `Outcome(ok=False)` with the attempt history intact, because the runner
    still needs to verify a "failed" write in case it actually landed.
    """
    attempts: list[Attempt] = []

    for number in range(1, max_attempts + 1):
        started = time.perf_counter()
        try:
            value = fn()
        except BaseException as exc:  # noqa: BLE001 - classified below
            latency = (time.perf_counter() - started) * 1000.0
            status = http_status_of(exc)
            retryable = is_retryable(exc)
            last = number >= max_attempts

            attempt = Attempt(
                number=number,
                status="failed" if (last or not retryable) else "retrying",
                latency_ms=latency,
                http_status=status,
                error=f"{type(exc).__name__}: {exc}",
                op=op,
            )

            if retryable and not last:
                delay = backoff_delay(number, rng)
                attempt.slept_ms = delay * 1000.0
                attempts.append(attempt)
                sleep(delay)
                continue

            attempts.append(attempt)
            return Outcome(
                ok=False,
                error=attempt.error,
                http_status=status,
                attempts=attempts,
            )

        latency = (time.perf_counter() - started) * 1000.0
        attempts.append(Attempt(number=number, status="ok", latency_ms=latency, op=op))
        return Outcome(ok=True, value=value, attempts=attempts)

    # Unreachable: the loop either returns or exhausts into the last-attempt
    # branch above. Kept explicit so a future edit to the loop cannot fall off
    # the end and silently return None.
    raise AssertionError(f"retry.call exhausted without returning (op={op!r})")
