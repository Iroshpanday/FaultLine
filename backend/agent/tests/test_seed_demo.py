import pytest
from django.core.management import call_command

from commerce.models import Order

pytestmark = pytest.mark.django_db


def test_seed_demo_can_run_twice_without_duplicates():
    call_command("seed_demo")
    call_command("seed_demo")

    assert Order.objects.filter(store__slug="momo-mart").count() == 4
    assert Order.objects.get(store__slug="momo-mart", number=123).status == "shipped"
