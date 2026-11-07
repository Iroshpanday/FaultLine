import uuid

from django.db import models
from django.db.models import Q


class Store(models.Model):
    """A tenant: one online shop using Faultline. Everything else belongs to a store."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=~Q(name=""), name="store_name_not_empty"),
        ]

    def __str__(self):
        return self.name
