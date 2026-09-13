"""Request -> effects.

Hardcoded shapes for now. This module exists so the runner, the WAL, the risk
gate and read-back can be exercised end to end before any model is in the loop.

TODO: replace the regex table below with LLM parsing.
      Call Anthropic (claude-opus-5) with a tool-use schema whose tool is
      `emit_effects(effects: list[Effect])`, so the model must return structured
      effects rather than prose. Constraints that must survive the swap:
        * The model proposes effects; it never calls a provider directly.
        * Every emitted effect needs a deterministic idempotency_key derived
          from the logical target (order id, product key) — never from the
          model's output text, which varies between attempts.
        * A model that cannot resolve a target to exactly one record must emit
          zero effects and a refusal reason, not a guess. That is the ambiguous
          product-name path (SCENARIOS.md #14).
        * The risk gate still runs on whatever the model returns. The model is
          not trusted to police its own scope.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .types import Effect

#: Catalog known to the planner. Mirrors what seed.py writes to Stripe/Notion.
CATALOG: dict[str, dict] = {
    "starter": {"display": "Starter", "cents": 2900},
    "pro": {"display": "Pro", "cents": 9900},
    "team": {"display": "Team", "cents": 24900},
    "enterprise": {"display": "Enterprise", "cents": 99900},
}

#: Order ID -> amount in cents. Mirrors the payments seed.py creates.
KNOWN_ORDERS: dict[str, int] = {"4417": 9900, "4418": 2900, "4419": 24900}

#: Names that match more than one catalog entry and must never be guessed.
AMBIGUOUS_NAMES: dict[str, list[str]] = {
    "professional": ["Pro", "Team (Notion row reads 'Team / Professional Seats')"],
}

DEFAULT_CHANNEL = "SLACK_CHANNEL_ID"


@dataclass
class PlanResult:
    """Either a list of effects, or a refusal with a reason."""

    effects: list[Effect] = field(default_factory=list)
    refusal: str | None = None

    @property
    def refused(self) -> bool:
        return self.refusal is not None


# -- request shapes ---------------------------------------------------------

_REFUND_RE = re.compile(r"\brefund\b.*?\border\s+(?P<order>\d{3,})", re.IGNORECASE | re.DOTALL)
_REPRICE_RE = re.compile(
    r"\bmove\s+(?P<product>[A-Za-z][A-Za-z ]*?)\s+to\s+\$?(?P<dollars>\d+(?:\.\d{2})?)",
    re.IGNORECASE,
)


def plan_request(request: str) -> PlanResult:
    """Map a request to effects, or refuse."""
    text = (request or "").strip()
    if not text:
        return PlanResult(refusal="Empty request.")

    match = _REFUND_RE.search(text)
    if match:
        return _plan_refund(match.group("order"), text)

    match = _REPRICE_RE.search(text)
    if match:
        return _plan_reprice(match.group("product").strip(), match.group("dollars"), text)

    return PlanResult(
        refusal=(
            f"No known request shape matches {text!r}. The planner only handles "
            f"refunds ('refund order <id>') and repricing ('move <product> to $<n>') "
            f"until LLM parsing lands. Refusing rather than guessing."
        )
    )


def _plan_refund(order_id: str, request: str) -> PlanResult:
    if order_id not in KNOWN_ORDERS:
        return PlanResult(
            refusal=(
                f"Order {order_id} is not in the known order set "
                f"({', '.join(sorted(KNOWN_ORDERS))}). Refusing to refund an "
                f"order the planner cannot resolve to one payment."
            )
        )

    amount = KNOWN_ORDERS[order_id]
    reason = _extract_reason(request) or "customer refund requested"
    dollars = f"${amount / 100:,.2f}"

    return PlanResult(
        effects=[
            Effect(
                app="stripe",
                action="refund_payment",
                params={"order_id": order_id, "amount_cents": amount, "reason": reason},
                idempotency_key=f"stripe:refund:order-{order_id}",
            ),
            Effect(
                app="notion",
                action="append_audit_row",
                params={
                    "order_id": order_id,
                    "amount_cents": amount,
                    "reason": reason,
                    "kind": "refund",
                },
                idempotency_key=f"notion:audit:refund-order-{order_id}",
            ),
            Effect(
                app="slack",
                action="post_message",
                params={
                    "channel": DEFAULT_CHANNEL,
                    "text": f"Refunded order {order_id} ({dollars}). Reason: {reason}.",
                },
                idempotency_key=f"slack:post:refund-order-{order_id}",
            ),
        ]
    )


def _plan_reprice(product: str, dollars: str, request: str) -> PlanResult:
    key = product.strip().lower()

    if key in AMBIGUOUS_NAMES:
        candidates = ", ".join(AMBIGUOUS_NAMES[key])
        return PlanResult(
            refusal=(
                f"Product name {product!r} is ambiguous between: {candidates}. "
                f"Refusing to guess which one the request meant."
            )
        )

    if key not in CATALOG:
        return PlanResult(
            refusal=(
                f"Product {product!r} is not in the catalog "
                f"({', '.join(c['display'] for c in CATALOG.values())})."
            )
        )

    cents = int(round(float(dollars) * 100))
    display = CATALOG[key]["display"]
    previous_cents = CATALOG[key]["cents"]

    return PlanResult(
        effects=[
            Effect(
                app="stripe",
                action="create_price",
                params={
                    "product_key": key,
                    "unit_amount_cents": cents,
                    "currency": "usd",
                    "interval": "month",
                },
                idempotency_key=f"stripe:price:{key}-{cents}",
            ),
            Effect(
                app="notion",
                action="update_catalog_row",
                params={
                    "name": display,
                    "price": cents // 100,
                    "previous_price": previous_cents // 100,
                },
                idempotency_key=f"notion:catalog:{key}-{cents}",
            ),
            Effect(
                app="slack",
                action="post_message",
                params={
                    "channel": DEFAULT_CHANNEL,
                    "text": (
                        f"{display} pricing is now ${cents / 100:,.0f}/month "
                        f"(was ${previous_cents / 100:,.0f})."
                    ),
                },
                idempotency_key=f"slack:post:price-{key}-{cents}",
            ),
        ]
    )


def _extract_reason(request: str) -> str | None:
    match = re.search(r"\breason\b[:\s]+(?P<reason>.+)", request, re.IGNORECASE)
    if match:
        return match.group("reason").strip().rstrip(".")
    if re.search(r"\blog the reason\b", request, re.IGNORECASE):
        return "logged at operator request"
    return None
