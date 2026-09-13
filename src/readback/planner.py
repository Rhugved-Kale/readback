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
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from . import seed as _seed
from .types import Effect

#: Catalog known to the planner. Mirrors what seed.py writes to Stripe/Notion.
CATALOG: dict[str, dict] = {
    "starter": {"display": "Starter", "cents": 2900},
    "pro": {"display": "Pro", "cents": 9900},
    "team": {"display": "Team", "cents": 24900},
    "enterprise": {"display": "Enterprise", "cents": 99900},
}

#: Order ID -> amount in cents. Mirrors the payments seed.py creates.
#:
#: 4417-4419 are the demo orders. 9001-9020 are the test/eval range, all at the
#: same amount -- the live suite and the eval harness refund those and never the
#: demo ones, because a refund cannot be undone. The range bounds are imported
#: from seed.py rather than repeated, so the two cannot drift apart and leave
#: the planner refusing an order the seed just created.
KNOWN_ORDERS: dict[str, int] = {
    "4417": 9900,
    "4418": 2900,
    "4419": 24900,
    **{
        str(n): _seed.TEST_ORDER_AMOUNT_CENTS
        for n in range(_seed.TEST_ORDER_LOW, _seed.TEST_ORDER_HIGH + 1)
    },
}

#: Names that match more than one catalog entry and must never be guessed.
AMBIGUOUS_NAMES: dict[str, list[str]] = {
    "professional": ["Pro", "Team (Notion row reads 'Team / Professional Seats')"],
}

DEFAULT_CHANNEL = "SLACK_CHANNEL_ID"


#: Enumerates candidate orders for a time window. Returns
#: [{"order_id": str, "amount_cents": int, "created": datetime}, ...].
OrderResolver = Callable[[datetime], list[dict]]

#: Orders reserved for the eval harness, never included in a bulk enumeration.
EVAL_ORDER_LOW, EVAL_ORDER_HIGH = 9001, 9020

_UNIT_DAYS = {"day": 1, "week": 7, "month": 30}


@dataclass
class PlanResult:
    """Either a list of effects, or a refusal with a reason."""

    effects: list[Effect] = field(default_factory=list)
    refusal: str | None = None
    #: Free-form detail the Slack layer surfaces on a hold: the enumerated
    #: window, how many eval-range orders were excluded, the dollar total.
    enumeration: dict[str, Any] = field(default_factory=dict)

    @property
    def refused(self) -> bool:
        return self.refusal is not None


# -- request shapes ---------------------------------------------------------

_REFUND_RE = re.compile(r"\brefund\b.*?\border\s+(?P<order>\d{3,})", re.IGNORECASE | re.DOTALL)
#: Bulk refund over a TIME WINDOW: "refund everything from last week",
#: "refund all orders from the last 14 days". Distinct from the explicit-list
#: shape below because the target set is not named -- it has to be enumerated
#: from the provider before anyone can judge the blast radius.
_WINDOW_REFUND_RE = re.compile(
    r"\brefund\b[^.]*?\b(?:everything|all|every)\b[^.]*?\bfrom\b\s+"
    r"(?:the\s+)?(?:last|past|previous)\s+"
    r"(?:(?P<count>\d+)\s+)?(?P<unit>day|days|week|weeks|month|months)\b",
    re.IGNORECASE,
)

#: Bulk refund of an explicit order list: "Refund orders 4419, 4417 and 9001 in
#: full." Named orders only -- an unbounded phrasing is caught by the risk gate
#: before this ever matters. Emits one refund per order and NO audit/Slack
#: effect, because a bulk refund is a different shape from the single-order
#: flow and padding it would trip the record-count rule before the money rule.
_BULK_REFUND_RE = re.compile(
    r"\brefund\s+orders?\s+(?P<orders>[\d,\s]+(?:and\s+\d+)?)\s*\bin\s+full\b",
    re.IGNORECASE,
)

#: Bulk archive with an explicit count: "Archive the 9 cancelled Q3 orders and
#: post a summary." The count is stated, so the record-count rule is what should
#: fire -- not the unbounded-scope rule.
_BULK_ARCHIVE_RE = re.compile(
    r"\barchive\s+the\s+(?P<count>\d+)\s+[\w\s]*?\borders?\b",
    re.IGNORECASE,
)

_REPRICE_RE = re.compile(
    r"\bmove\s+(?P<product>[A-Za-z][A-Za-z ]*?)\s+to\s+\$?(?P<dollars>\d+(?:\.\d{2})?)",
    re.IGNORECASE,
)


def plan_request(request: str, order_resolver: OrderResolver | None = None) -> PlanResult:
    """Map a request to effects, or refuse.

    `order_resolver` is how the time-window shape enumerates its targets. It is
    injected rather than imported so this module stays pure and offline by
    default: with no resolver the window shape produces zero effects and says
    why, which is exactly what the eval harness and the unit tests see. Only
    the Slack app supplies a live, READ-ONLY Stripe reader.
    """
    text = (request or "").strip()
    if not text:
        return PlanResult(refusal="Empty request.")

    match = _WINDOW_REFUND_RE.search(text)
    if match:
        return _plan_window_refund(
            count=int(match.group("count") or 1),
            unit=match.group("unit").lower().rstrip("s"),
            resolver=order_resolver,
        )

    match = _BULK_REFUND_RE.search(text)
    if match:
        return _plan_bulk_refund(match.group("orders"), text)

    match = _BULK_ARCHIVE_RE.search(text)
    if match:
        return _plan_bulk_archive(int(match.group("count")), text)

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


def _plan_window_refund(
    count: int, unit: str, resolver: OrderResolver | None
) -> PlanResult:
    """Enumerate every refundable order in a time window, concretely.

    The point of this shape is that the risk gate cannot judge "everything from
    last week" without knowing what everything IS. So the window is resolved to
    actual order ids and actual amounts first, and the gate is then handed a
    plan it can weigh. The reply names the ids rather than a count, because
    "would refund 14 orders" is not something a human can sanity-check and
    "would refund 4417, 4418, ..., totalling $1,240.00" is.

    Enumeration is READ-ONLY. Nothing here writes.
    """
    days = _UNIT_DAYS[unit] * max(count, 1)
    since = datetime.now(timezone.utc) - timedelta(days=days)
    window = f"last {count} {unit}{'s' if count != 1 else ''}"

    if resolver is None:
        # Offline: no provider to enumerate against. Zero effects, and the risk
        # gate still holds the request on unbounded scope.
        return PlanResult(
            refusal=(
                f"Refunding {window} needs a live enumeration of the orders in that "
                f"window, and no order resolver is configured. Refusing rather than "
                f"guessing the blast radius."
            ),
            enumeration={"window": window, "since": since.isoformat(), "resolved": False},
        )

    candidates = resolver(since)

    excluded = [
        c for c in candidates
        if str(c["order_id"]).isdigit()
        and EVAL_ORDER_LOW <= int(c["order_id"]) <= EVAL_ORDER_HIGH
    ]
    included = [c for c in candidates if c not in excluded]

    total_cents = sum(int(c["amount_cents"]) for c in included)
    order_ids = [str(c["order_id"]) for c in included]

    enumeration = {
        "window": window,
        "since": since.isoformat(),
        "resolved": True,
        "order_ids": order_ids,
        "total_cents": total_cents,
        "excluded_eval_orders": [str(c["order_id"]) for c in excluded],
        "excluded_count": len(excluded),
    }

    if not included:
        return PlanResult(
            refusal=(
                f"No refundable orders found in the {window} "
                f"({len(excluded)} eval-range order(s) excluded)."
            ),
            enumeration=enumeration,
        )

    return PlanResult(
        effects=[
            Effect(
                app="stripe",
                action="refund_payment",
                params={
                    "order_id": str(c["order_id"]),
                    "amount_cents": int(c["amount_cents"]),
                    "reason": f"bulk refund, {window}",
                },
                idempotency_key=f"stripe:refund:order-{c['order_id']}",
            )
            for c in included
        ],
        enumeration=enumeration,
    )


def _plan_bulk_refund(orders_text: str, request: str) -> PlanResult:
    """One refund effect per named order.

    Deliberately emits no audit or Slack effect. The point of this shape is to
    let the risk gate weigh the MONEY being moved; adding two fixed effects per
    run would push a four-order refund over the record-count limit first and the
    money rule would never be reached.
    """
    order_ids = re.findall(r"\d{3,}", orders_text)
    unknown = [o for o in order_ids if o not in KNOWN_ORDERS]
    if unknown:
        return PlanResult(
            refusal=(
                f"Orders {', '.join(unknown)} are not in the known order set. "
                f"Refusing to refund orders the planner cannot resolve to a payment."
            )
        )
    if not order_ids:
        return PlanResult(refusal="No order IDs found in the bulk refund request.")

    return PlanResult(
        effects=[
            Effect(
                app="stripe",
                action="refund_payment",
                params={
                    "order_id": order_id,
                    "amount_cents": KNOWN_ORDERS[order_id],
                    "reason": "bulk refund requested",
                },
                idempotency_key=f"stripe:refund:order-{order_id}",
            )
            for order_id in order_ids
        ]
    )


def _plan_bulk_archive(count: int, request: str) -> PlanResult:
    """One archive effect per record, plus a summary post.

    The order ids are synthetic: this shape exists so the record-count rule is
    exercised on a plan that is genuinely too large, and the gate holds it
    before a single write is attempted. Nothing here is ever applied in a
    passing run, by design.
    """
    if count <= 0:
        return PlanResult(refusal="Archive request names zero records.")

    effects = [
        Effect(
            app="stripe",
            action="archive_order",
            params={"order_id": f"q3-{index:03d}"},
            idempotency_key=f"stripe:archive:q3-{index:03d}",
        )
        for index in range(1, count + 1)
    ]
    effects.append(
        Effect(
            app="slack",
            action="post_message",
            params={
                "channel": DEFAULT_CHANNEL,
                "text": f"Archived {count} cancelled Q3 orders.",
            },
            idempotency_key=f"slack:post:archive-q3-{count}",
        )
    )
    return PlanResult(effects=effects)


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
