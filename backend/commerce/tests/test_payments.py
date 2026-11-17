"""The fake payment gateway. Plain Python: no database, no network."""

from decimal import Decimal

import pytest

from commerce.payments import FakePaymentGateway, PaymentTimeout

AMOUNT = Decimal("1250.00")


def refund(gateway, key=None):
    return gateway.refund(order_ref="order-123", amount=AMOUNT, currency="NPR", idempotency_key=key)


def test_a_normal_refund_pays_out_once_and_returns_a_receipt():
    gateway = FakePaymentGateway()

    receipt = refund(gateway)

    assert receipt.provider_ref == "re_0001"
    assert gateway.total_paid_out == AMOUNT


def test_a_late_reply_still_pays_out_the_money():
    # Rush hour: the provider refunds the customer, but we only see a timeout.
    gateway = FakePaymentGateway(late_replies=1)

    with pytest.raises(PaymentTimeout):
        refund(gateway)

    assert gateway.total_paid_out == AMOUNT  # the money left, though we were told nothing


def test_retrying_without_a_key_pays_out_twice():
    # The bug E1 is about, at the provider's level: a blind retry is a second refund.
    gateway = FakePaymentGateway(late_replies=1)

    with pytest.raises(PaymentTimeout):
        refund(gateway)
    refund(gateway)  # "it timed out, let's try again"

    assert gateway.total_paid_out == AMOUNT * 2


def test_retrying_with_the_same_key_returns_the_first_refund():
    # What a real provider offers: same key, same refund, no second payout.
    gateway = FakePaymentGateway(late_replies=1)

    with pytest.raises(PaymentTimeout):
        refund(gateway, key="refund-order-123")
    receipt = refund(gateway, key="refund-order-123")

    assert receipt.provider_ref == "re_0001"
    assert gateway.total_paid_out == AMOUNT
