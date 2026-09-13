"""Stripe adapter against the live API.

Two effects:

    stripe.refund_payment(order_id, reason)      IRREVERSIBLE
    stripe.update_price(product_key, new_amount_cents)   reversible

The asymmetry between them is the whole point of the Effect.reversible flag.
A price change can be put back exactly. A refund cannot: the money has left the
account, and no Stripe call un-refunds a charge. So refunds are sorted to run
last, and a run that has to roll back after one committed reports
PARTIAL_MANUAL_REMEDIATION with the refund id, rather than claiming it undid
something it did not.
"""

from __future__ import annotations

import os
from typing import Any

import stripe as stripe_sdk

from ..core import retry
from ..types import STATUS_OK, Effect, EffectResult, IrreversibleEffect
from .base import Adapter
from .live_base import LiveAdapter


class StripeAdapter(LiveAdapter, Adapter):
    name = "stripe"

    ACTIONS = {
        "refund_payment": "refund",
        "update_price": "price",
    }

    def __init__(self, client=None, api_key: str | None = None, run_id: str = "") -> None:
        self.client = client or stripe_sdk
        self.run_id = run_id
        key = api_key or os.environ.get("STRIPE_SECRET_KEY", "")
        if key:
            self.client.api_key = key

    # -- plan --------------------------------------------------------------

    def plan(self, request) -> list[Effect]:
        """Stripe's share of a request.

        The module-level planner already produces the full cross-app plan, so
        this exists to satisfy the Adapter contract and to let Stripe effects be
        built in isolation (tests, replay). Pure: no writes, no provider reads.
        """
        effects: list[Effect] = []
        for effect in getattr(request, "effects", request) or []:
            if isinstance(effect, Effect) and effect.app == self.name:
                effects.append(effect)
        return effects

    # -- apply -------------------------------------------------------------

    def apply(self, effect: Effect) -> EffectResult:
        action = self.canonical(effect.action)
        if action == "refund_payment":
            return self._apply_refund(effect)
        if action == "update_price":
            return self._apply_price(effect)
        return self._skipped(effect, f"stripe adapter does not handle {effect.action!r}")

    def _apply_refund(self, effect: Effect) -> EffectResult:
        """Refund the PaymentIntent behind an order id.

        Irreversible by construction, declared BEFORE the write goes out so the
        flag is already correct if the process dies between here and commit.
        """
        effect.reversible = False

        order_id = str(effect.params["order_id"])
        found = retry.call(lambda: self._find_payment_intent(order_id), op="pi.search")
        if not found.ok:
            return self._failed(effect, found, "could not resolve order to a PaymentIntent")
        intent = found.value
        if intent is None:
            return self._failed(
                effect,
                found,
                f"no PaymentIntent carries metadata order_id={order_id!r}",
            )

        # Pre-write state. A refund has no inverse, so this is captured for the
        # receipt and for verify()'s expected arithmetic, not for rollback.
        effect.prior_state = {
            "payment_intent": intent.id,
            "amount_received": int(intent.amount_received or 0),
            "already_refunded_cents": self._refunded_total(intent.id),
            "irreversible_reason": "a refund cannot be un-refunded through any Stripe API",
        }

        amount = int(effect.params.get("amount_cents") or intent.amount_received)
        reason = effect.params.get("reason", "")

        outcome = retry.call(
            lambda: self.client.Refund.create(
                payment_intent=intent.id,
                amount=amount,
                metadata={"order_id": order_id, "run_id": self.run_id, "reason": reason[:400]},
                # Stripe's NATIVE idempotency. A retry of this exact key is
                # absorbed upstream and returns the original Refund rather than
                # issuing a second one -- the one provider here where duplicate
                # suppression does not depend on our own bookkeeping.
                idempotency_key=f"{effect.idempotency_key}:refund",
            ),
            op="refund.create",
        )
        if not outcome.ok:
            return self._failed(effect, outcome, "Refund.create")

        refund = outcome.value
        return self._ok(effect, outcome, {
            "refund_id": refund.id,
            "payment_intent": intent.id,
            "amount": refund.amount,
            "status": refund.status,
        })

    def _apply_price(self, effect: Effect) -> EffectResult:
        """Repoint a product at a new monthly USD price.

        Three writes behind one effect: create the new price, make it the
        product default, archive the old one. prior_state is captured before
        any of them so compensate() can put all three back.
        """
        product_key = str(effect.params["product_key"])
        new_amount = int(
            effect.params.get("new_amount_cents")
            or effect.params.get("unit_amount_cents")
        )

        found = retry.call(lambda: self._find_product(product_key), op="product.search")
        if not found.ok:
            return self._failed(effect, found, "could not resolve product_key")
        product = found.value
        if product is None:
            return self._failed(
                effect, found, f"no product carries metadata product_key={product_key!r}"
            )

        # PRE-WRITE CAPTURE. Without this the effect cannot be reversed, so an
        # effect that reaches here without it must not claim to be reversible.
        old_price_id = self._default_price_id(product)
        old_amount = None
        if old_price_id:
            old_price = self.client.Price.retrieve(old_price_id)
            old_amount = old_price.unit_amount

        if old_price_id is None:
            # Nothing to restore to: reversing would mean inventing a default
            # price that never existed. Declare it rather than pretend.
            effect.reversible = False
            effect.prior_state = {
                "product_id": product.id,
                "default_price_id": None,
                "irreversible_reason": "product had no default_price to restore",
            }
        else:
            effect.reversible = True
            effect.prior_state = {
                "product_id": product.id,
                "default_price_id": old_price_id,
                "default_price_amount": old_amount,
            }

        created = retry.call(
            lambda: self.client.Price.create(
                product=product.id,
                currency="usd",
                unit_amount=new_amount,
                recurring={"interval": "month"},
                metadata={"product_key": product_key, "run_id": self.run_id},
                idempotency_key=f"{effect.idempotency_key}:price",
            ),
            op="price.create",
        )
        if not created.ok:
            return self._failed(effect, created, "Price.create")
        new_price = created.value
        effect.prior_state["new_price_id"] = new_price.id

        promoted = retry.call(
            lambda: self.client.Product.modify(
                product.id,
                default_price=new_price.id,
                idempotency_key=f"{effect.idempotency_key}:default",
            ),
            op="product.modify",
        )
        if not promoted.ok:
            return self._failed(effect, promoted, "Product.modify(default_price)")

        # Archive the old price LAST. Stripe refuses to archive a price that is
        # still a product default, so the order here is load-bearing.
        archived = None
        if old_price_id:
            archived = retry.call(
                lambda: self.client.Price.modify(
                    old_price_id,
                    active=False,
                    idempotency_key=f"{effect.idempotency_key}:archive",
                ),
                op="price.archive",
            )
            if not archived.ok:
                return self._failed(effect, archived, "Price.modify(archive old)")

        merged = retry.Outcome(
            ok=True,
            attempts=created.attempts + promoted.attempts + (archived.attempts if archived else []),
        )
        return self._ok(effect, merged, {
            "product_id": product.id,
            "new_price_id": new_price.id,
            "new_amount": new_price.unit_amount,
            "archived_price_id": old_price_id,
        })

    # -- verify ------------------------------------------------------------

    def verify(self, effect: Effect) -> tuple[bool, str]:
        """Re-read live Stripe state.

        HARD RULE: everything below issues a NEW request to Stripe. Nothing here
        touches the EffectResult from apply(), the Refund/Price object apply()
        received, or any adapter-held cache. The only inputs are the Effect
        (which the WAL can reconstruct after a crash) and what Stripe says right
        now, so a restarted process running this method reaches the same verdict
        as this one.
        """
        action = self.canonical(effect.action)
        if action == "refund_payment":
            return self._verify_refund(effect)
        if action == "update_price":
            return self._verify_price(effect)
        return False, f"stripe adapter cannot verify {effect.action!r}"

    def _verify_refund(self, effect: Effect) -> tuple[bool, str]:
        order_id = str(effect.params["order_id"])
        expected_refund = int(effect.params.get("amount_cents") or 0)

        def check(attempt: int) -> tuple[bool, str]:
            # FRESH retrieve. Resolved from order_id rather than from a stored
            # pi_ id so this works from a bare WAL record after a restart.
            intent = self._find_payment_intent(order_id)
            if intent is None:
                return False, f"no PaymentIntent for order_id={order_id!r} (read attempt {attempt})"

            # FRESH list of refunds. Deliberately not the Refund object apply()
            # got back -- that response is the thing under suspicion.
            refunds = self.client.Refund.list(payment_intent=intent.id, limit=100).data
            succeeded = [r for r in refunds if r.status == "succeeded"]
            refunded_total = sum(int(r.amount) for r in succeeded)
            received = int(intent.amount_received or 0)
            remaining = received - refunded_total

            expected_remaining = received - expected_refund
            if not succeeded:
                return False, (
                    f"stripe.refund_payment: PaymentIntent {intent.id} shows NO succeeded "
                    f"refund; amount_received={received} unchanged (read attempt {attempt})"
                )
            if remaining != expected_remaining:
                return False, (
                    f"stripe.refund_payment: expected amount_received - refunded to be "
                    f"{expected_remaining} (={received} - {expected_refund}), live Stripe "
                    f"reports {remaining} (refunded {refunded_total} across "
                    f"{len(succeeded)} succeeded refund(s)) (read attempt {attempt})"
                )
            return True, (
                f"stripe.refund_payment: live read of {intent.id} confirms refunded="
                f"{refunded_total}, amount_received - refunded = {remaining}, "
                f"{len(succeeded)} refund(s) all status=succeeded (read attempt {attempt})"
            )

        return self._reread(check)

    def _verify_price(self, effect: Effect) -> tuple[bool, str]:
        product_key = str(effect.params["product_key"])
        expected = int(
            effect.params.get("new_amount_cents")
            or effect.params.get("unit_amount_cents")
        )

        def check(attempt: int) -> tuple[bool, str]:
            # FRESH retrieve with default_price expanded, resolved from the
            # product_key in the Effect -- not from anything apply() returned.
            product = self._find_product(product_key, expand=["data.default_price"])
            if product is None:
                return False, f"no product for product_key={product_key!r} (read attempt {attempt})"
            price = getattr(product, "default_price", None)
            if price is None or isinstance(price, str):
                return False, (
                    f"stripe.update_price: product {product.id} has no expanded "
                    f"default_price (read attempt {attempt})"
                )
            if int(price.unit_amount) != expected:
                return False, (
                    f"stripe.update_price: expected default_price.unit_amount={expected}, "
                    f"live Stripe reports {price.unit_amount} on price {price.id} "
                    f"(read attempt {attempt})"
                )
            if price.currency != "usd":
                return False, (
                    f"stripe.update_price: expected currency=usd, live Stripe reports "
                    f"{price.currency!r} (read attempt {attempt})"
                )
            return True, (
                f"stripe.update_price: live read of product {product.id} confirms "
                f"default_price={price.id} unit_amount={price.unit_amount} currency=usd "
                f"(read attempt {attempt})"
            )

        return self._reread(check)

    # -- compensate --------------------------------------------------------

    def compensate(self, effect: Effect) -> EffectResult:
        action = self.canonical(effect.action)

        if action == "refund_payment":
            # NO inverse exists and none is attempted. Raising here is the
            # honest answer: the runner catches it, reverses everything else,
            # and emits PARTIAL_MANUAL_REMEDIATION naming the object below.
            prior = effect.prior_state or {}
            raise IrreversibleEffect(
                f"Stripe refund on order {effect.params.get('order_id')} cannot be reversed: "
                f"the money has already left the account and Stripe exposes no un-refund. "
                f"A human must decide whether to re-charge the customer.",
                app=self.name,
                object_id=str(prior.get("payment_intent") or effect.params.get("order_id", "")),
            )

        if action == "update_price":
            return self._compensate_price(effect)

        return self._skipped(effect, f"nothing to compensate for {effect.action!r}")

    def _compensate_price(self, effect: Effect) -> EffectResult:
        """Restore the previous default price, exactly.

        Idempotent: if the product is already pointing at the old price, this
        reports 'skipped' rather than erroring, per the Adapter contract.
        """
        prior = effect.prior_state or {}
        product_id = prior.get("product_id")
        old_price_id = prior.get("default_price_id")
        new_price_id = prior.get("new_price_id")

        if not product_id or not old_price_id:
            raise IrreversibleEffect(
                f"Stripe price change on {effect.params.get('product_key')!r} cannot be "
                f"reversed: no prior default_price was captured before the write.",
                app=self.name,
                object_id=str(product_id or new_price_id or ""),
            )

        live = self.client.Product.retrieve(product_id)
        if self._default_price_id(live) == old_price_id:
            return self._skipped(effect, "product already points at the prior price", {
                "product_id": product_id, "default_price_id": old_price_id,
            })

        # Unarchive first: Stripe will not accept an inactive price as default.
        unarchive = retry.call(
            lambda: self.client.Price.modify(old_price_id, active=True), op="price.unarchive"
        )
        if not unarchive.ok:
            return self._failed(effect, unarchive, "Price.modify(unarchive old)")

        restore = retry.call(
            lambda: self.client.Product.modify(product_id, default_price=old_price_id),
            op="product.restore",
        )
        if not restore.ok:
            return self._failed(effect, restore, "Product.modify(restore default_price)")

        archived_new = None
        if new_price_id:
            archived_new = retry.call(
                lambda: self.client.Price.modify(new_price_id, active=False),
                op="price.archive_new",
            )

        merged = retry.Outcome(
            ok=True,
            attempts=unarchive.attempts + restore.attempts
            + (archived_new.attempts if archived_new else []),
        )
        return self._ok(effect, merged, {
            "restored_default_price_id": old_price_id,
            "archived_price_id": new_price_id,
            "note": "prior default price restored and re-activated; new price archived",
        })

    # -- live reads used by cross-checks -----------------------------------

    def live_default_price(self, product_key: str) -> dict[str, Any] | None:
        """Fresh read of a product's default price. Used by crosscheck.py.

        Public because a cross-check must read Stripe from OUTSIDE the Stripe
        adapter's own verify path -- the point is that a different app's claim
        is checked against this, not that Stripe agrees with itself.
        """
        product = self._find_product(product_key, expand=["data.default_price"])
        if product is None:
            return None
        price = getattr(product, "default_price", None)
        if price is None or isinstance(price, str):
            return None
        return {
            "product_id": product.id,
            "price_id": price.id,
            "unit_amount": int(price.unit_amount),
            "currency": price.currency,
        }

    def live_refund_total(self, order_id: str) -> dict[str, Any] | None:
        """Fresh read of succeeded refund cents for an order. Used by crosscheck."""
        intent = self._find_payment_intent(str(order_id))
        if intent is None:
            return None
        refunds = self.client.Refund.list(payment_intent=intent.id, limit=100).data
        succeeded = [r for r in refunds if r.status == "succeeded"]
        return {
            "payment_intent": intent.id,
            "refunded_cents": sum(int(r.amount) for r in succeeded),
            "refund_ids": [r.id for r in succeeded],
        }

    # -- internals ---------------------------------------------------------

    def _find_payment_intent(self, order_id: str):
        results = self.client.PaymentIntent.search(
            query=f"metadata['order_id']:'{order_id}'", limit=100
        ).data
        usable = [pi for pi in results if pi.status in ("succeeded", "requires_capture")]
        return usable[0] if usable else (results[0] if results else None)

    def _find_product(self, product_key: str, expand: list[str] | None = None):
        kwargs: dict[str, Any] = {
            "query": f"metadata['product_key']:'{product_key}'",
            "limit": 1,
        }
        if expand:
            kwargs["expand"] = expand
        results = self.client.Product.search(**kwargs).data
        return results[0] if results else None

    @staticmethod
    def _default_price_id(product) -> str | None:
        """Default price id, whether Stripe returned it expanded or as a string.

        getattr rather than .get(): a StripeObject is not a Mapping and raises
        on .get, which is exactly how the first seed run died.
        """
        value = getattr(product, "default_price", None)
        if value is None:
            return None
        return value if isinstance(value, str) else value.id

    def _refunded_total(self, payment_intent_id: str) -> int:
        refunds = self.client.Refund.list(payment_intent=payment_intent_id, limit=100).data
        return sum(int(r.amount) for r in refunds if r.status == "succeeded")
