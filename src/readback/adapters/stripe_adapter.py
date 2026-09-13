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

import hashlib
import json
import os
from typing import Any

import stripe as stripe_sdk

from ..core import retry
from ..types import STATUS_OK, Effect, EffectResult, IrreversibleEffect
from .base import Adapter
from .live_base import LiveAdapter


#: How many objects a list-fallback will page through before giving up. Bounded
#: so a miss degrades into a clear error instead of walking an entire account.
FALLBACK_SCAN_LIMIT = 500


def find_product_by_key(client, product_key: str, expand: list[str] | None = None):
    """Find a product by metadata product_key and return AUTHORITATIVE fields.

    Two distinct Stripe consistency problems, two distinct answers, and neither
    is a sleep:

    1. MISS. Stripe's search index is asynchronous, so an object created seconds
       ago is routinely absent from Product.search -- which returns an empty
       page rather than an error. Fallback: a paginated Product.list filtered
       client-side. list reads the primary store and is immediately consistent.
       It costs more calls, which is why it is second rather than first.

    2. STALE HIT. Worse and less obvious: search can RETURN the object while
       serving an out-of-date copy of it. A product repriced moments ago comes
       back with its previous default_price, and no amount of re-reading the
       search index fixes it -- observed here still stale on the third attempt,
       over a second after the write. Sleeping longer is just a guess about
       someone else's indexing latency.

       So search/list is used ONLY to resolve product_key -> product id, which
       never changes. Every field value comes from Product.retrieve on that id,
       which reads the primary store. That is the difference between "the index
       thinks Team costs $249" and "Team costs $249".

    `expand` is in retrieve form (e.g. ["default_price"]).
    """
    search_expand = [f"data.{e}" for e in expand] if expand else None

    product_id = None
    kwargs: dict[str, Any] = {"query": f"metadata['product_key']:'{product_key}'", "limit": 1}
    if search_expand:
        kwargs["expand"] = search_expand
    hits = client.Product.search(**kwargs).data
    if hits:
        product_id = hits[0].id
    else:
        list_kwargs: dict[str, Any] = {"limit": 100}
        scanned = 0
        for candidate in client.Product.list(**list_kwargs).auto_paging_iter():
            scanned += 1
            if scanned > FALLBACK_SCAN_LIMIT:
                break
            if _meta(candidate).get("product_key") == product_key:
                product_id = candidate.id
                break

    if product_id is None:
        return None

    # Authoritative read. Never trust the search copy's field values.
    retrieve_kwargs: dict[str, Any] = {}
    if expand:
        retrieve_kwargs["expand"] = expand
    return client.Product.retrieve(product_id, **retrieve_kwargs)


def find_payment_intents_by_order(client, order_id: str) -> list:
    """All PaymentIntents carrying metadata order_id, from search AND list.

    Always merges. The search index is never allowed to short-circuit the list
    call, however confident its answer looks.

    WHY, precisely: a STALE NON-EMPTY search result is more dangerous than an
    empty one, because it looks like an answer. Empty triggers a fallback and
    the caller recovers. A stale set of three already-refunded intents, with
    the freshly created refundable one still missing from the index, is
    indistinguishable from a complete answer -- so the caller confidently picks
    a spent intent and the refund fails. Observed live: two of four demo resets
    left the new intent invisible to search for over a minute while `list`
    returned it immediately.

    This is the same class of bug as trusting a write response. The provider
    returned something well-formed and plausible, and the mistake was treating
    "the provider replied" as "the provider told the truth". Read-back exists
    because a response is evidence, not proof; the search index deserves exactly
    the same suspicion, and for the same reason.

    `list` reads the primary store and is immediately consistent, so where the
    two disagree the list copy wins.

    Ordering: refundable intents first, then newest first. That serves both
    callers without either having to know about the other -- apply() wants an
    intent it can still refund, and verify() re-resolving after a refund wants
    the one that was just refunded, which is the newest.
    """
    merged: dict[str, Any] = {}

    # Search: fast, indexed, possibly stale. Contributes, never decides.
    for intent in client.PaymentIntent.search(
        query=f"metadata['order_id']:'{order_id}'", limit=100
    ).data:
        merged[intent.id] = intent

    # List: authoritative. Overwrites the search copy where both exist, because
    # the search copy may describe an older version of the same object.
    scanned = 0
    for intent in client.PaymentIntent.list(limit=100).auto_paging_iter():
        scanned += 1
        if scanned > FALLBACK_SCAN_LIMIT:
            break
        if _meta(intent).get("order_id") == str(order_id):
            merged[intent.id] = intent

    def sort_key(intent) -> tuple[int, int]:
        refundable = 0 if _is_refundable(client, intent) else 1
        return (refundable, -int(getattr(intent, "created", 0) or 0))

    return sorted(merged.values(), key=sort_key)


def _is_refundable(client, intent) -> bool:
    """True when this intent succeeded and has no succeeded refund against it."""
    if getattr(intent, "status", None) != "succeeded":
        return False
    refunds = client.Refund.list(payment_intent=intent.id, limit=100).data
    return not any(r.status == "succeeded" for r in refunds)


def idem_key(effect_key: str, op: str, body: dict) -> str:
    """Stripe idempotency key bound to both the logical write AND the body.

    Stripe remembers a key together with the exact body it was first used with,
    for 24 hours, and answers any reuse with a different body with a 400 rather
    than a replay. A key derived only from the logical write therefore becomes a
    liability the moment the request shape changes: every run for the next day
    fails on a key poisoned by the previous code's body. That is not
    hypothetical -- it is what happened here when run_id was dropped from the
    metadata.

    Hashing the body fixes both directions at once:
      * same logical write, same body  -> same key, so a retry after a crash or
        a timeout is still absorbed upstream, which is the property that
        matters;
      * body changes at all            -> new key, so a schema change can never
        collide with a key the old code already spent.
    """
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:12]
    return f"{effect_key}:{op}:{digest}"


def _meta(obj) -> dict:
    """Metadata as a plain dict. A StripeObject is not a Mapping and has no .get."""
    meta = getattr(obj, "metadata", None)
    if meta is None:
        return {}
    try:
        return meta.to_dict()
    except AttributeError:
        return dict(meta)


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

        # ONLY stable identifiers in the body. run_id and the free-text reason
        # vary between runs and belong in the Notion audit row, not here.
        refund_body = {
            "payment_intent": intent.id,
            "amount": amount,
            "metadata": {"order_id": order_id},
        }
        outcome = retry.call(
            # Stripe's NATIVE idempotency. A retry of this exact key is absorbed
            # upstream and returns the original Refund rather than issuing a
            # second one -- the one provider here where duplicate suppression
            # does not depend on our own bookkeeping.
            lambda: self.client.Refund.create(
                **refund_body,
                idempotency_key=idem_key(effect.idempotency_key, "refund", refund_body),
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

        price_body = {
            "product": product.id,
            "currency": "usd",
            "unit_amount": new_amount,
            "recurring": {"interval": "month"},
            "metadata": {"product_key": product_key},
        }
        created = retry.call(
            lambda: self.client.Price.create(
                **price_body,
                idempotency_key=idem_key(effect.idempotency_key, "price", price_body),
            ),
            op="price.create",
        )
        if not created.ok:
            return self._failed(effect, created, "Price.create")
        new_price = created.value
        effect.prior_state["new_price_id"] = new_price.id

        # Do NOT trust `new_price.active` from the line above.
        #
        # An idempotent replay returns the price AS FIRST CREATED -- active=True
        # -- even when a later run's compensation has since archived it. The
        # response describes a moment in the past, not the current object. Read
        # it back fresh instead, which is the same rule verify() follows and the
        # reason this project exists; believing the write's own response here
        # cost three flaky live runs.
        #
        # Reusing the price rather than minting a new one is deliberate: it
        # stops a repeated reprice from littering the product with near
        # identical prices.
        live_price = self.client.Price.retrieve(new_price.id)
        if not live_price.active:
            reactivated = retry.call(
                lambda: self.client.Price.modify(new_price.id, active=True),
                op="price.reactivate",
            )
            if not reactivated.ok:
                return self._failed(effect, reactivated, "Price.modify(reactivate replayed)")

        # NO idempotency key on this modify, deliberately.
        #
        # An idempotency key makes Stripe REPLAY the first response without
        # re-performing the operation. That is exactly right for a create,
        # where running twice would mint a second object. It is exactly wrong
        # for "set default_price to X": a later run replays the cached 200,
        # Stripe never actually moves the default, and the next step then fails
        # trying to archive a price that is still the default. Observed here.
        #
        # Setting a field to a specific value is already idempotent by nature --
        # doing it twice leaves the same state and creates nothing. It needs no
        # key, and giving it one converts a safe repeat into a silent no-op.
        promoted = retry.call(
            lambda: self.client.Product.modify(product.id, default_price=new_price.id),
            op="product.modify",
        )
        if not promoted.ok:
            return self._failed(effect, promoted, "Product.modify(default_price)")

        # Archive the old price LAST. Stripe refuses to archive a price that is
        # still a product default, so the order here is load-bearing -- and the
        # promote above must have actually taken effect, not been replayed.
        # Re-read the product to confirm before archiving, rather than assuming
        # the modify did what it said.
        archived = None
        if old_price_id and old_price_id != new_price.id:
            live_default = self._default_price_id(self.client.Product.retrieve(product.id))
            if live_default == old_price_id:
                return self._failed(
                    effect,
                    retry.merge(created, promoted),
                    f"default_price is still {old_price_id} after promoting {new_price.id}; "
                    f"refusing to archive the live default price",
                )
        if old_price_id and old_price_id != new_price.id:
            # Same reasoning as the promote above: a field assignment is
            # naturally idempotent, so no key.
            archived = retry.call(
                lambda: self.client.Price.modify(old_price_id, active=False),
                op="price.archive",
            )
            if not archived.ok:
                return self._failed(effect, archived, "Price.modify(archive old)")

        merged = retry.merge(created, promoted, archived)
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
            product = self._find_product(product_key, expand=["default_price"])
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
            # Establish that there IS something to reverse before declaring it
            # irreversible.
            #
            # Compensation now runs for effects whose apply() FAILED as well as
            # those that committed, because a timeout after commit leaves a real
            # write behind. That means this method can be reached for a refund
            # that never actually happened -- and announcing "the money is gone,
            # a human must decide whether to re-charge the customer" about a
            # refund that was never issued is a false alarm of the worst kind.
            # So: fresh read first, and only then the honest refusal.
            order_id = str(effect.params.get("order_id", ""))
            live = self.live_refund_total(order_id)
            if live is None or live["refunded_cents"] == 0:
                return self._skipped(
                    effect,
                    f"no succeeded refund exists on order {order_id}; "
                    f"nothing to reverse and nothing for a human to undo",
                    {"order_id": order_id},
                )

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

        merged = retry.merge(unarchive, restore, archived_new)
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
        product = self._find_product(product_key, expand=["default_price"])
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
        results = find_payment_intents_by_order(self.client, order_id)
        usable = [pi for pi in results if pi.status in ("succeeded", "requires_capture")]
        return usable[0] if usable else (results[0] if results else None)

    def _find_product(self, product_key: str, expand: list[str] | None = None):
        return find_product_by_key(self.client, product_key, expand=expand)

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
