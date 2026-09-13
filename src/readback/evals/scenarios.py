"""The 14 scenarios from SCENARIOS.md, as executable definitions.

Each scenario declares three things the harness needs and nothing else:

  request        what the operator asked for
  injection      any STRUCTURAL interference (state drifting under the run, a
                 mid-run crash). Provider-level faults come from faults.py and
                 are applied on top by the matrix, so every scenario is run
                 under every fault profile.
  expected_final_state
                 the ground truth the oracle judges against: exactly which
                 records must exist in each fake provider when a CORRECT run
                 has finished, and with what field values.

`expected_final_state` is deliberately exhaustive per app: the oracle asserts
the store holds exactly these keys, no more and no fewer. An extra record is a
double write or an un-reversed effect; a missing one is a dropped write. Both
are wrong, and a rule that only checked for presence would miss half of that.

Note on the refuse scenarios: their correct end state is an EMPTY store in every
app, because a held request must cost zero writes. That makes "held but executed
anyway" a state-level failure the oracle catches on its own, without needing to
read the receipt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

#: Amounts mirror planner.KNOWN_ORDERS.
REFUND_4417 = {"order_id": "4417", "amount_cents": 9900, "reason": "logged at operator request"}
REFUND_4418 = {"order_id": "4418", "amount_cents": 2900, "reason": "logged at operator request"}

OUTCOME_SUCCESS = "success"
OUTCOME_REFUSE = "refuse"
OUTCOME_COMPENSATE = "compensate"


@dataclass
class Injection:
    """Structural interference, distinct from a provider fault.

    `drift_app`/`drift_key`/`drift_changes` mutate live state behind the
    runner's back after the write lands -- the silent-divergence case.
    `crash_on_app` raises inside that app's apply(), after which the harness
    replays the same run_id to exercise WAL recovery.
    """

    drift_app: str | None = None
    drift_key: str | None = None
    drift_changes: dict[str, Any] = field(default_factory=dict)
    crash_on_app: str | None = None


@dataclass
class Scenario:
    id: int
    name: str
    request: str
    expected_outcome: str
    expected_final_state: dict[str, dict[str, dict[str, Any]]]
    injection: Injection = field(default_factory=Injection)
    notes: str = ""

    @property
    def label(self) -> str:
        return f"S{self.id:02d}"


def _empty() -> dict[str, dict]:
    """Correct end state for a refused run, and for a fully compensated one."""
    return {"stripe": {}, "notion": {}, "slack": {}}


def _refund_state(order: str, amount: int, reason: str) -> dict[str, dict]:
    dollars = f"${amount / 100:,.2f}"
    return {
        "stripe": {
            f"stripe:refund:order-{order}": {
                "order_id": order, "amount_cents": amount, "reason": reason,
            }
        },
        "notion": {
            f"notion:audit:refund-order-{order}": {
                "order_id": order, "amount_cents": amount, "reason": reason, "kind": "refund",
            }
        },
        "slack": {
            f"slack:post:refund-order-{order}": {
                "channel": "SLACK_CHANNEL_ID",
                "text": f"Refunded order {order} ({dollars}). Reason: {reason}.",
            }
        },
    }


def _reprice_state(key: str, display: str, cents: int, previous_cents: int) -> dict[str, dict]:
    return {
        "stripe": {
            f"stripe:price:{key}-{cents}": {
                "product_key": key, "unit_amount_cents": cents,
                "currency": "usd", "interval": "month",
            }
        },
        "notion": {
            f"notion:catalog:{key}-{cents}": {
                "name": display, "price": cents // 100,
                "previous_price": previous_cents // 100,
            }
        },
        "slack": {
            f"slack:post:price-{key}-{cents}": {
                "channel": "SLACK_CHANNEL_ID",
                "text": (
                    f"{display} pricing is now ${cents / 100:,.0f}/month "
                    f"(was ${previous_cents / 100:,.0f})."
                ),
            }
        },
    }


REFUND_REQUEST = "Refund order 4417 and log the reason."
REPRICE_REQUEST = "Move Pro to $79 everywhere."

SCENARIOS: list[Scenario] = [
    Scenario(
        id=1, name="refund_happy_path", request=REFUND_REQUEST,
        expected_outcome=OUTCOME_SUCCESS,
        expected_final_state=_refund_state("4417", 9900, "logged at operator request"),
    ),
    Scenario(
        id=2, name="reprice_happy_path", request=REPRICE_REQUEST,
        expected_outcome=OUTCOME_SUCCESS,
        expected_final_state=_reprice_state("pro", "Pro", 7900, 9900),
    ),
    Scenario(
        id=3, name="unbounded_scope_refused",
        request="Refund everything from last week.",
        expected_outcome=OUTCOME_REFUSE,
        expected_final_state=_empty(),
        notes="unbounded scope; zero effects may be applied",
    ),
    Scenario(
        id=4, name="refund_error_after_write", request=REFUND_REQUEST,
        expected_outcome=OUTCOME_SUCCESS,
        expected_final_state=_refund_state("4417", 9900, "logged at operator request"),
        notes="500 after the write landed; read-back must promote FAILED -> COMMITTED",
    ),
    Scenario(
        id=5, name="refund_timeout_after_commit", request=REFUND_REQUEST,
        expected_outcome=OUTCOME_SUCCESS,
        expected_final_state=_refund_state("4417", 9900, "logged at operator request"),
        notes="timeout on a committed write; must not retry into a duplicate",
    ),
    Scenario(
        id=6, name="refund_rate_limit_storm", request=REFUND_REQUEST,
        expected_outcome=OUTCOME_SUCCESS,
        expected_final_state=_refund_state("4417", 9900, "logged at operator request"),
        notes="429s then success; retries must not fan out into duplicate posts",
    ),
    Scenario(
        id=7, name="refund_stale_read", request=REFUND_REQUEST,
        expected_outcome=OUTCOME_SUCCESS,
        expected_final_state=_refund_state("4417", 9900, "logged at operator request"),
        notes="first reads return pre-write state; verify must not accept them",
    ),
    Scenario(
        id=8, name="reprice_error_after_write", request=REPRICE_REQUEST,
        expected_outcome=OUTCOME_SUCCESS,
        expected_final_state=_reprice_state("pro", "Pro", 7900, 9900),
    ),
    Scenario(
        id=9, name="reprice_stale_read", request=REPRICE_REQUEST,
        expected_outcome=OUTCOME_SUCCESS,
        expected_final_state=_reprice_state("pro", "Pro", 7900, 9900),
    ),
    Scenario(
        id=10, name="reprice_verify_failure_compensates", request=REPRICE_REQUEST,
        expected_outcome=OUTCOME_COMPENSATE,
        # Correct behaviour is a total rollback, so the correct end state is
        # empty. A run that leaves the drifted catalog row behind is wrong even
        # if it reported failure -- that is partial_state, and the oracle sees it.
        expected_final_state=_empty(),
        injection=Injection(
            drift_app="notion",
            drift_key="notion:catalog:pro-7900",
            drift_changes={"price": 99},
        ),
        notes="Notion silently retains $99; every committed effect must be reversed",
    ),
    Scenario(
        id=11, name="crash_midrun_then_retry",
        request="Refund order 4418 and log the reason.",
        expected_outcome=OUTCOME_SUCCESS,
        expected_final_state=_refund_state("4418", 2900, "logged at operator request"),
        injection=Injection(crash_on_app="slack"),
        notes="crash after the first commit; replay must not double-write",
    ),
    Scenario(
        id=12, name="over_money_limit_refused",
        # Four named orders totalling $546. Stays at 4 effects on purpose so the
        # MONEY rule fires and not the record-count rule.
        request="Refund orders 4419, 4417, 9001 and 9002 in full.",
        expected_outcome=OUTCOME_REFUSE,
        expected_final_state=_empty(),
        notes="over the $500 money limit",
    ),
    Scenario(
        id=13, name="over_record_count_refused",
        request="Archive the 9 cancelled Q3 orders and post a summary.",
        expected_outcome=OUTCOME_REFUSE,
        expected_final_state=_empty(),
        notes="10 effects, over the 5-effect limit",
    ),
    Scenario(
        id=14, name="ambiguous_product_refused",
        request="Move Professional to $79.",
        expected_outcome=OUTCOME_REFUSE,
        expected_final_state=_empty(),
        notes="'Professional' is ambiguous between Pro and Team",
    ),
]

assert len(SCENARIOS) == 14, f"expected 14 scenarios, have {len(SCENARIOS)}"


def by_id(scenario_id: int) -> Scenario:
    for scenario in SCENARIOS:
        if scenario.id == scenario_id:
            return scenario
    raise KeyError(f"no scenario {scenario_id}")
