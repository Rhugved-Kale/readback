"""Stripe adapter. Interface only — no implementation yet.

Every method names the exact API call it will make, so the read-back semantics
are pinned down before any code exists.
"""

from __future__ import annotations

from ..types import Effect, EffectResult
from .base import Adapter


class StripeAdapter(Adapter):
    name = "stripe"

    def __init__(self, client=None, **kwargs) -> None:
        # TODO: accept a configured `stripe` module/client; read STRIPE_SECRET_KEY
        #       from the environment when `client` is None.
        self.client = client

    def plan(self, request) -> list[Effect]:
        # TODO: no API call. Map the parsed request onto Stripe effects:
        #       refund_payment  -> needs order_id + amount_cents
        #       create_price    -> needs product_key + unit_amount_cents
        #       Resolve order_id -> PaymentIntent via PaymentIntent.search(
        #           query="metadata['order_id']:'4417'") at plan time so the
        #       effect carries a concrete `pi_...` and planning stays pure.
        raise NotImplementedError

    def apply(self, effect: Effect) -> EffectResult:
        # TODO: refund_payment -> stripe.Refund.create(
        #           payment_intent=effect.params["payment_intent"],
        #           amount=effect.params["amount_cents"],
        #           idempotency_key=effect.idempotency_key)
        # TODO: create_price   -> stripe.Price.create(
        #           product=effect.params["product_id"], currency="usd",
        #           unit_amount=effect.params["unit_amount_cents"],
        #           recurring={"interval": "month"},
        #           idempotency_key=effect.idempotency_key)
        raise NotImplementedError

    def verify(self, effect: Effect) -> tuple[bool, str]:
        # TODO: refund_payment -> stripe.PaymentIntent.retrieve(pi_id) as a FRESH
        #       call, then assert status == "succeeded" and
        #       amount_received - amount_refunded matches the expectation.
        #       Do NOT read the Refund object returned by apply().
        # TODO: create_price   -> stripe.Price.list(product=product_id, active=True)
        #       and assert a price exists with unit_amount == expected,
        #       currency == "usd", recurring.interval == "month".
        raise NotImplementedError

    def compensate(self, effect: Effect) -> EffectResult:
        # TODO: create_price   -> stripe.Price.modify(price_id, active=False)
        #       (prices cannot be deleted; deactivation is the inverse).
        # TODO: refund_payment -> NO true inverse exists. Do not attempt one.
        #       Record the irreversibility in the EffectResult and let the
        #       receipt say plainly that the money is gone and needs a human.
        raise NotImplementedError
