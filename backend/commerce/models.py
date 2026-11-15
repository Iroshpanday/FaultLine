import uuid

from django.db import models
from django.db.models import Q
from django.utils import timezone


class Customer(models.Model):
    """A shopper of one store. Email/name are personal data (handled in E10)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey("stores.Store", on_delete=models.PROTECT, related_name="customers")
    external_ref = models.CharField(max_length=100)  # the shop's own customer id, e.g. "C-1001"
    email = models.EmailField()
    name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["store", "external_ref"], name="customer_external_ref_unique_per_store"
            ),
        ]

    def __str__(self):
        return f"{self.external_ref} ({self.store})"


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey("stores.Store", on_delete=models.PROTECT, related_name="orders")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    number = models.PositiveIntegerField()  # what the customer sees: "order #123"
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)  # ISO code: "NPR", "USD", "EUR"
    placed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["store", "number"],
                name="order_number_unique_per_store",
            ),
            models.CheckConstraint(
                condition=Q(total__gte=0),
                name="order_total_not_negative",
            ),
            models.CheckConstraint(
                condition=Q(status__in=OrderStatus.values),
                name="order_status_valid",
            ),
        ]

        indexes = [
            # Latest orders for a store
            models.Index(
                fields=["store", "placed_at"],
                name="order_store_placed_at_idx",
            ),
        ]
