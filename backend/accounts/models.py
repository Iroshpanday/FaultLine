import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Project user. Empty on purpose: it exists so we can add fields later
    without swapping AUTH_USER_MODEL mid-project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
