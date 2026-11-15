"""Create fake demo data for the agent: Momo Mart with a few orders.

    python manage.py seed_demo

Safe to run many times: it only creates what is missing (get_or_create).
All data is fake; free models may log prompts, so never seed real customers.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from commerce.models import Customer, Order, OrderStatus
from stores.models import Store

DEMO_ORDERS = [
    # number, status, total (NPR), days ago
    (123, OrderStatus.SHIPPED, "2450.00", 3),
    (124, OrderStatus.PENDING, "899.00", 0),
    (125, OrderStatus.DELIVERED, "5200.00", 10),
    (126, OrderStatus.CANCELLED, "1500.00", 6),
]


class Command(BaseCommand):
    help = "Create fake demo data (Momo Mart + orders #123-#126). Safe to re-run."

    @transaction.atomic
    def handle(self, *args, **options):
        store, _ = Store.objects.get_or_create(slug="momo-mart", defaults={"name": "Momo Mart"})
        customer, _ = Customer.objects.get_or_create(
            store=store,
            external_ref="DEMO-1",
            defaults={"email": "demo.customer@example.com", "name": "Demo Customer"},
        )

        created = 0
        now = timezone.now()
        for number, status, total, days_ago in DEMO_ORDERS:
            _, was_created = Order.objects.get_or_create(
                store=store,
                number=number,
                defaults={
                    "customer": customer,
                    "status": status,
                    "total": Decimal(total),
                    "currency": "NPR",
                    "placed_at": now - timedelta(days=days_ago),
                },
            )
            created += was_created

        self.stdout.write(self.style.SUCCESS(
            f"{store.name}: {created} new order(s), {len(DEMO_ORDERS) - created} already there."
        ))
