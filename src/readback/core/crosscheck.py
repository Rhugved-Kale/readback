"""Cross-app assertions: read a fact from a DIFFERENT app than the one that wrote it.

Per-effect verify() answers "did my write land in the app I wrote it to?" That
catches dropped writes. It cannot catch the failure that actually hurts in ops
work: every individual write landing, while the apps end up disagreeing with
each other. Stripe says Pro is $79, Notion still says $99, Slack has announced
both. Three green verifications, one incoherent system.

So each assertion here deliberately crosses a boundary:

  * the price check reads the number Notion holds and compares it to the number
    STRIPE holds -- neither app is asked to confirm its own claim;
  * the refund check reads the amount Notion recorded and compares it to the
    refund total STRIPE reports.

A cross-check failure is treated exactly like a verify failure: the run does
not succeed, and compensation runs. That is the point -- a coherent rollback is
better than a system left half-repriced.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from ..types import Effect

#: Money comparisons are cents-exact. The tolerance exists only to absorb IEEE
#: float representation of dollar values (99.00 round-tripping through Notion),
#: never to paper over a real discrepancy -- half a cent is far below the
#: smallest difference any real mismatch can produce.
EPSILON = 1e-6


@dataclass
class CrossCheck:
    """One assertion spanning two providers."""

    name: str
    reads_from: str      # the app being asked
    written_by: str      # the app that made the claim being tested
    description: str
    check: Callable[[], tuple[bool, str]]

    def evaluate(self) -> tuple[bool, str]:
        try:
            return self.check()
        except BaseException as exc:  # noqa: BLE001
            return False, f"cross-check raised {type(exc).__name__}: {exc}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "reads_from": self.reads_from,
            "written_by": self.written_by,
            "description": self.description,
        }


def supported(adapters: Mapping[str, Any]) -> bool:
    """True only when the adapters expose live cross-reads.

    FakeAdapter deliberately does not implement `live_*`, so fake runs produce
    zero cross-checks and the in-memory tests stay meaningful as tests of the
    loop rather than of Stripe. Cross-checks are a live-adapter feature.
    """
    stripe = adapters.get("stripe")
    notion = adapters.get("notion")
    return bool(
        stripe is not None
        and notion is not None
        and hasattr(stripe, "live_default_price")
        and hasattr(notion, "live_catalog_row")
    )


def build(
    adapters: Mapping[str, Any], effects: list[Effect], run_id: str
) -> list[CrossCheck]:
    """Derive the cross-checks implied by the effects that just ran."""
    if not supported(adapters):
        return []

    stripe = adapters["stripe"]
    notion = adapters["notion"]
    checks: list[CrossCheck] = []

    for effect in effects:
        action = effect.action
        if action in ("update_price", "create_price"):
            checks.append(_price_coherence(stripe, notion, effect))
        elif action == "refund_payment":
            checks.append(_refund_coherence(stripe, notion, effect, run_id))

    return checks


# -- the assertions ---------------------------------------------------------


def _price_coherence(stripe, notion, effect: Effect) -> CrossCheck:
    """Stripe's live default price must equal what Notion's catalog claims.

    Two independent comparisons, both crossing the boundary:
      unit_amount / 100 == Notion Price (number)
      default_price.id  == Notion Stripe Price ID (text)
    """
    product_key = str(effect.params.get("product_key") or "").lower()
    display = product_key.capitalize()

    def check() -> tuple[bool, str]:
        live_stripe = stripe.live_default_price(product_key)      # fresh Stripe read
        live_notion = notion.live_catalog_row(display)            # fresh Notion read

        if live_stripe is None:
            return False, f"cross-check: Stripe has no default price for {product_key!r}"
        if live_notion is None:
            return False, f"cross-check: Notion has no catalog row named {display!r}"

        stripe_dollars = live_stripe["unit_amount"] / 100.0
        notion_price = live_notion["price"]
        if notion_price is None:
            return False, (
                f"cross-check FAILED: Stripe says {display} is ${stripe_dollars:,.2f} "
                f"but the Notion catalog Price cell is empty"
            )
        if abs(float(notion_price) - stripe_dollars) > EPSILON:
            return False, (
                f"cross-check FAILED: Stripe default_price is {live_stripe['unit_amount']} "
                f"cents (${stripe_dollars:,.2f}) but Notion catalog Price reads "
                f"{notion_price}. The two systems disagree about what {display} costs."
            )

        if live_notion["stripe_price_id"] != live_stripe["price_id"]:
            return False, (
                f"cross-check FAILED: Stripe's live default price is "
                f"{live_stripe['price_id']} but Notion's Stripe Price ID column reads "
                f"{live_notion['stripe_price_id']!r}. Notion points at a stale price."
            )

        return True, (
            f"cross-check: Stripe default_price {live_stripe['price_id']} = "
            f"{live_stripe['unit_amount']} cents (${stripe_dollars:,.2f}) matches Notion "
            f"catalog Price {notion_price} and Stripe Price ID "
            f"{live_notion['stripe_price_id']} for {display}"
        )

    return CrossCheck(
        name=f"price_coherence:{product_key}",
        reads_from="stripe+notion",
        written_by="stripe",
        description=(
            f"Stripe default_price unit_amount/100 == Notion catalog Price, and "
            f"Notion Stripe Price ID == live Stripe default price id, for {display}"
        ),
        check=check,
    )


def _refund_coherence(stripe, notion, effect: Effect, run_id: str) -> CrossCheck:
    """Notion's audit Amount must equal Stripe's live refunded total.

    The audit row is Notion's claim about what Stripe did. This asks Stripe.
    """
    order_id = str(effect.params.get("order_id") or "")

    def check() -> tuple[bool, str]:
        live_stripe = stripe.live_refund_total(order_id)   # fresh Stripe read
        live_notion = notion.live_audit_row(run_id)        # fresh Notion read

        if live_stripe is None:
            return False, f"cross-check: Stripe has no PaymentIntent for order {order_id}"
        if live_notion is None:
            return False, (
                f"cross-check: Notion has no single audit row for run {run_id} "
                f"(zero, or more than one)"
            )

        stripe_dollars = live_stripe["refunded_cents"] / 100.0
        notion_amount = live_notion["amount"]
        if notion_amount is None:
            return False, (
                f"cross-check FAILED: Stripe refunded ${stripe_dollars:,.2f} on order "
                f"{order_id} but the Notion audit row's Amount cell is empty"
            )
        if abs(float(notion_amount) - stripe_dollars) > EPSILON:
            return False, (
                f"cross-check FAILED: Stripe reports {live_stripe['refunded_cents']} cents "
                f"refunded (${stripe_dollars:,.2f}) on order {order_id}, but the Notion "
                f"audit row records Amount={notion_amount}. The audit log misstates what "
                f"actually happened to the money."
            )

        return True, (
            f"cross-check: Stripe refunded {live_stripe['refunded_cents']} cents "
            f"(${stripe_dollars:,.2f}) on order {order_id} via "
            f"{', '.join(live_stripe['refund_ids']) or 'no refund'}, matching the Notion "
            f"audit row Amount={notion_amount} for run {run_id}"
        )

    return CrossCheck(
        name=f"refund_coherence:{order_id}",
        reads_from="stripe+notion",
        written_by="notion",
        description=(
            f"Notion audit row Amount == live Stripe refunded total / 100 for order {order_id}"
        ),
        check=check,
    )
