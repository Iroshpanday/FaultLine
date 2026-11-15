from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError

from commerce.factories import CustomerFactory, OrderFactory
from stores.factories import StoreFactory

pytestmark = pytest.mark.django_db


def test_order_and_its_customer_belong_to_the_same_store():
    order = OrderFactory()

    assert order.customer.store == order.store


def test_same_order_number_is_allowed_in_different_stores():
    OrderFactory(number=123)
    OrderFactory(number=123)  # a different store (SubFactory creates a new one)


def test_duplicate_order_number_in_the_same_store_is_rejected():
    first = OrderFactory(number=123)

    with pytest.raises(IntegrityError):
        OrderFactory(number=123, store=first.store, customer=first.customer)


def test_negative_total_is_rejected():
    with pytest.raises(IntegrityError):
        OrderFactory(total=Decimal("-1.00"))


def test_unknown_status_is_rejected():
    with pytest.raises(IntegrityError):
        OrderFactory(status="shiped")  # typo on purpose


def test_store_with_customers_cannot_be_deleted():
    customer = CustomerFactory()

    with pytest.raises(ProtectedError):
        customer.store.delete()
