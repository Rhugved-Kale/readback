"""The fake and the real adapters must agree on the Adapter contract.

These tests exist because they already failed once in a way that cost real
analysis time. FakeAdapter.compensate ignored `Effect.reversible` while
StripeAdapter raised IrreversibleEffect for the same input. When the rollback
walk widened to cover FAILED effects, the eval matrix reported a 13.6%
forbidden_effect_rate for readback_on -- a number that measured the test
double, not the runner. Production never violated the invariant.

A fake that is more permissive than production does not merely fail to catch
bugs; it manufactures ones that are not there. So the contract is pinned here,
and both implementations are driven through the same assertions.

No network: the Stripe adapter is driven against a minimal double.
"""

from __future__ import annotations

import pytest

from readback.adapters.fake import FakeAdapter
from readback.adapters.stripe_adapter import StripeAdapter
from readback.types import STATUS_SKIPPED, Effect, IrreversibleEffect


class _Obj(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key) from None


class _Meta(dict):
    def to_dict(self):
        return dict(self)


class _List:
    def __init__(self, data):
        self.data = data


class _Page:
    def __init__(self, data):
        self._data = data

    def auto_paging_iter(self):
        return iter(self._data)


class _StripeDouble:
    """Minimal Stripe stand-in. `refunded` controls whether a refund exists."""

    api_key = None

    def __init__(self, refunded: bool):
        self._refunded = refunded
        outer = self

        class PaymentIntent:
            @staticmethod
            def search(**_kw):
                return _List([
                    _Obj(id="pi_1", status="succeeded", amount_received=9900,
                         metadata=_Meta(order_id="4417"))
                ])

            @staticmethod
            def list(**_kw):
                return _Page([])

        class Refund:
            @staticmethod
            def list(payment_intent, limit=100):
                if not outer._refunded:
                    return _List([])
                return _List([_Obj(id="re_1", amount=9900, status="succeeded")])

        self.PaymentIntent = PaymentIntent
        self.Refund = Refund


def _refund_effect() -> Effect:
    return Effect(
        app="stripe",
        action="refund_payment",
        params={"order_id": "4417", "amount_cents": 9900},
        idempotency_key="stripe:refund:order-4417",
    )


def _reversible_effect() -> Effect:
    return Effect(
        app="stripe",
        action="create_price",
        params={"product_key": "pro", "unit_amount_cents": 7900},
        idempotency_key="stripe:price:pro-7900",
    )


def test_refund_is_irreversible_by_construction():
    """Both adapters see the same flag, because it comes from the Effect."""
    assert _refund_effect().reversible is False
    assert _reversible_effect().reversible is True


def test_both_adapters_raise_when_an_irreversible_effect_exists():
    """The contract: a committed irreversible effect raises, it is never undone."""
    effect = _refund_effect()

    fake = FakeAdapter(name="stripe")
    fake.apply(effect)  # the write exists
    with pytest.raises(IrreversibleEffect) as fake_exc:
        fake.compensate(effect)

    real = StripeAdapter(client=_StripeDouble(refunded=True), api_key="sk_test_x")
    with pytest.raises(IrreversibleEffect) as real_exc:
        real.compensate(effect)

    # Both must name an object a human can act on.
    assert fake_exc.value.object_id
    assert real_exc.value.object_id
    assert fake_exc.value.app == real_exc.value.app == "stripe"


def test_both_adapters_skip_when_there_is_nothing_to_reverse():
    """Absence is checked BEFORE irreversibility, in both implementations.

    Announcing that money is gone when no refund was ever issued is a false
    alarm, so 'nothing there' must win over 'cannot be undone'.
    """
    effect = _refund_effect()

    fake = FakeAdapter(name="stripe")  # nothing applied
    assert fake.compensate(effect).status == STATUS_SKIPPED

    real = StripeAdapter(client=_StripeDouble(refunded=False), api_key="sk_test_x")
    assert real.compensate(effect).status == STATUS_SKIPPED


def test_reversible_effects_are_compensated_normally_by_both():
    """The flag must not make every compensation refuse."""
    effect = _reversible_effect()

    fake = FakeAdapter(name="stripe")
    fake.apply(effect)
    assert fake.compensate(effect).status == "ok"
    assert effect.idempotency_key not in fake.store

    # The real adapter's price rollback needs prior_state; without it the
    # contract says raise rather than guess. Either way it must NOT silently
    # succeed at reversing something it cannot reverse.
    real = StripeAdapter(client=_StripeDouble(refunded=False), api_key="sk_test_x")
    with pytest.raises(IrreversibleEffect):
        real.compensate(effect)


def test_compensate_is_idempotent_in_the_fake():
    """Contract: compensating twice is a no-op, not an error."""
    effect = _reversible_effect()
    fake = FakeAdapter(name="stripe")
    fake.apply(effect)
    assert fake.compensate(effect).status == "ok"
    assert fake.compensate(effect).status == STATUS_SKIPPED
