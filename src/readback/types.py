"""Core value types shared by the planner, the runner, and every adapter."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

# Effect statuses as reported by an adapter's apply()/compensate().
STATUS_OK = "ok"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"

# Actions whose params["amount_cents"] represents money actually moving.
# The risk gate sums these; a price change is not money moved.
MONEY_MOVING_ACTIONS = frozenset({"refund_payment", "create_charge", "create_payout"})


@dataclass
class Effect:
    """A single intended write against exactly one provider.

    An Effect is the unit of everything: it is what the WAL logs, what the risk
    gate counts, what an adapter applies, what read-back verifies, and what
    compensation reverses. It must carry enough information to be re-applied or
    reversed by a fresh process that has only the WAL to go on.
    """

    app: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    idempotency_key: str = ""
    id: str = field(default_factory=lambda: f"eff_{uuid.uuid4().hex[:12]}")

    def __post_init__(self) -> None:
        if not self.idempotency_key:
            # Derived from the effect identity so a retry of the *same* logical
            # write produces the *same* key. Callers should normally pass an
            # explicit, stable key instead of relying on this.
            self.idempotency_key = f"{self.app}:{self.action}:{self.id}"

    @property
    def money_cents(self) -> int:
        """Money this effect moves, in cents. Zero for non-financial effects."""
        if self.action not in MONEY_MOVING_ACTIONS:
            return 0
        return int(self.params.get("amount_cents", 0))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "app": self.app,
            "action": self.action,
            "params": self.params,
            "idempotency_key": self.idempotency_key,
        }


@dataclass
class EffectResult:
    """What an adapter reports back from apply() or compensate().

    This is *evidence*, never proof. The runner records it in the receipt and
    uses it to decide WAL state, but a `status == "ok"` here never stands in for
    a read-back assertion, and a `status == "failed"` never proves the write
    did not land.
    """

    effect_id: str
    status: str
    provider_response: Any = None
    latency_ms: float = 0.0
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == STATUS_OK

    def to_dict(self) -> dict[str, Any]:
        return {
            "effect_id": self.effect_id,
            "status": self.status,
            "provider_response": self.provider_response,
            "latency_ms": round(self.latency_ms, 2),
            "error": self.error,
        }


@dataclass
class Postcondition:
    """One read-back assertion: a human-readable claim plus a live check.

    `check` takes no arguments and returns (passed, detail). It is expected to
    issue a fresh provider read every time it is called.
    """

    app: str
    description: str
    check: Callable[[], tuple[bool, str]]

    def evaluate(self) -> tuple[bool, str]:
        return self.check()

    def to_dict(self) -> dict[str, Any]:
        return {"app": self.app, "description": self.description}


@dataclass
class RunContext:
    """Identity and provenance for a single run.

    `run_id` is the join key for everything on disk: runs/{run_id}/wal.jsonl and
    runs/{run_id}/receipt.json. Re-running with an existing run_id is how crash
    recovery works — the WAL is replayed and committed effects are skipped.
    """

    request_text: str
    run_id: str = field(default_factory=lambda: f"run_{uuid.uuid4().hex[:12]}")
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "request_text": self.request_text,
            "started_at": self.started_at.isoformat(),
        }
