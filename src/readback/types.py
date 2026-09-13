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

# Actions with no provider inverse. Known at PLAN time, not discovered at apply
# time, because the runner has to sort irreversible effects last *before* it
# calls anything -- by the time an adapter could tell us, the ordering decision
# is already spent. Adapters may still downgrade an effect to irreversible
# during apply() (e.g. a product with no prior default_price to restore); they
# may not upgrade one listed here back to reversible.
IRREVERSIBLE_ACTIONS = frozenset({"refund_payment", "create_charge", "create_payout"})


class IrreversibleEffect(Exception):
    """Raised by compensate() for a write the provider cannot undo.

    Carries the provider object id a human needs in order to finish the job by
    hand. This is never swallowed into a generic failure: a run that cannot
    fully roll back must say so, name the object, and refuse to report success.
    """

    def __init__(self, message: str, *, app: str = "", object_id: str = "") -> None:
        super().__init__(message)
        self.app = app
        self.object_id = object_id


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

    #: False when the provider offers no true inverse for this write. A refund
    #: is the canonical case: money has left the account and no API call puts it
    #: back. Irreversible effects are sorted to run LAST (see runner) so that a
    #: reversible effect that is going to fail fails while rollback is still
    #: total, and a run that trips compensation after one has committed reports
    #: PARTIAL_MANUAL_REMEDIATION rather than claiming a clean rollback.
    reversible: bool = True

    #: The provider state this effect overwrote, captured by apply() BEFORE the
    #: write goes out. compensate() restores from here, so it must be captured
    #: even when nothing later reads it. None means "not captured yet"; an
    #: effect that reaches apply() with reversible=True and cannot capture its
    #: prior state must downgrade itself to reversible=False rather than commit
    #: a write it has no way to undo.
    prior_state: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.action in IRREVERSIBLE_ACTIONS:
            # Not overridable: no caller gets to declare a refund reversible.
            self.reversible = False
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
            "reversible": self.reversible,
            "prior_state": self.prior_state,
        }

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "Effect":
        """Rebuild an Effect from a WAL record.

        Compensation after a crash has nothing but the WAL to work from, so
        `prior_state` and `reversible` have to survive the round trip. Dropping
        them here would leave a restarted process able to see that a write
        happened but not what it overwrote.
        """
        return cls(
            app=record["app"],
            action=record["action"],
            params=record.get("params", {}),
            idempotency_key=record.get("idempotency_key", ""),
            id=record.get("effect_id", ""),
            reversible=record.get("reversible", True),
            prior_state=record.get("prior_state"),
        )


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
