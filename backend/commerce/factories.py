from decimal import Decimal

import factory

from stores.factories import StoreFactory

from .models import Customer, Order


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    store = factory.SubFactory(StoreFactory)
    external_ref = factory.Sequence(lambda n: f"C-{1000 + n}")
    email = factory.Sequence(lambda n: f"customer{n}@example.com")
    name = "Test Customer"


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    store = factory.SubFactory(StoreFactory)
    # The customer must belong to the SAME store as the order.
    customer = factory.SubFactory(CustomerFactory, store=factory.SelfAttribute("..store"))
    number = factory.Sequence(lambda n: 100 + n)
    total = Decimal("1000.00")
    currency = "NPR"
