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

# external_ref, email, name
CUSTOMERS = {
    "demo": ("DEMO-1", "demo.customer@example.com", "Demo Customer"),
    # A second shopper, so the demo can show one customer can't see another's order.
    "sita": ("DEMO-2", "sita.sharma@example.com", "Sita Sharma"),
}

DEMO_ORDERS = [
    # number, customer, status, total (NPR), days ago
    (123, "demo", OrderStatus.SHIPPED, "2450.00", 3),
    (124, "demo", OrderStatus.PENDING, "899.00", 0),
    (125, "demo", OrderStatus.DELIVERED, "5200.00", 10),
    (126, "demo", OrderStatus.CANCELLED, "1500.00", 6),
    (127, "sita", OrderStatus.SHIPPED, "1250.00", 2),
]


class Command(BaseCommand):
    help = "Create fake demo data (Momo Mart, 2 customers, orders #123-#127). Safe to re-run."

    @transaction.atomic
    def handle(self, *args, **options):
        store, _ = Store.objects.get_or_create(slug="momo-mart", defaults={"name": "Momo Mart"})
        customers = {
            key: Customer.objects.get_or_create(
                store=store, external_ref=ref, defaults={"email": email, "name": name}
            )[0]
            for key, (ref, email, name) in CUSTOMERS.items()
        }

        created = 0
        now = timezone.now()
        for number, customer_key, status, total, days_ago in DEMO_ORDERS:
            _, was_created = Order.objects.get_or_create(
                store=store,
                number=number,
                defaults={
                    "customer": customers[customer_key],
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
