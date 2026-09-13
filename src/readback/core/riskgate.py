"""Pre-flight gate. Decides whether a plan may be applied at all.

The gate runs after planning and before the first provider call, so a held
request costs exactly zero writes. It is intentionally blunt: it holds on
*shape* (unbounded scope, too many records, too much money) rather than trying
to judge intent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from ..types import Effect

# ---------------------------------------------------------------------------
# THRESHOLDS — every tunable lives here and nowhere else.
# ---------------------------------------------------------------------------

#: Maximum number of effects a single run may apply.
MAX_EFFECTS = 5

#: Maximum total money moved by one run, in cents ($500.00).
MAX_MONEY_CENTS = 50_000

#: Request shapes with no enumerable target set. Matching any of these holds the
#: run regardless of how few effects the planner happened to produce.
UNBOUNDED_SCOPE_PATTERNS: tuple[str, ...] = (
    r"\bevery\b",
    r"\ball\b",
    r"\beverything\b",
    r"\beach\b",
    r"\banything\b",
    r"\bany\s+(?:order|customer|invoice|subscription)\b",
    r"\bentire\b",
    r"\bbulk\b",
    r"\bfrom\s+last\s+(?:week|month|quarter|year)\b",
)

ALLOW = "allow"
HOLD = "hold"

# ---------------------------------------------------------------------------

_COMPILED = tuple(re.compile(p, re.IGNORECASE) for p in UNBOUNDED_SCOPE_PATTERNS)


@dataclass
class Decision:
    """The gate's verdict. `verdict` is ALLOW or HOLD."""

    verdict: str
    reason: str

    @property
    def allowed(self) -> bool:
        return self.verdict == ALLOW

    @property
    def held(self) -> bool:
        return self.verdict == HOLD

    def to_dict(self) -> dict[str, str]:
        return {"verdict": self.verdict, "reason": self.reason}


def evaluate(request: str, effects: Iterable[Effect]) -> Decision:
    """Hold on unbounded scope, too many effects, or too much money."""
    effects = list(effects)

    for pattern in _COMPILED:
        match = pattern.search(request or "")
        if match:
            return Decision(
                HOLD,
                f"Unbounded scope: the request says {match.group(0)!r}, which names no "
                f"enumerable set of records. A human must supply the explicit list.",
            )

    if len(effects) > MAX_EFFECTS:
        return Decision(
            HOLD,
            f"Record-count limit: the plan plans {len(effects)} effects, over the "
            f"limit of {MAX_EFFECTS}.",
        )

    total_cents = sum(effect.money_cents for effect in effects)
    if total_cents > MAX_MONEY_CENTS:
        return Decision(
            HOLD,
            f"Money limit: the plan moves ${total_cents / 100:,.2f}, over the limit of "
            f"${MAX_MONEY_CENTS / 100:,.2f}.",
        )

    return Decision(
        ALLOW,
        f"{len(effects)} effect(s), ${total_cents / 100:,.2f} moved; within all limits.",
    )
