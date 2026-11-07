import pytest
from django.db import IntegrityError

from stores.factories import StoreFactory

pytestmark = pytest.mark.django_db


def test_store_can_be_created():
    store = StoreFactory(name="Momo Mart")

    assert store.id is not None
    assert str(store) == "Momo Mart"


def test_empty_name_is_rejected_by_the_database():
    with pytest.raises(IntegrityError):
        StoreFactory(name="")


def test_duplicate_slug_is_rejected_by_the_database():
    StoreFactory(slug="momo-mart")

    with pytest.raises(IntegrityError):
        StoreFactory(slug="momo-mart")
