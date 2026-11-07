import factory

from .models import Store


class StoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Store

    name = factory.Sequence(lambda n: f"Store {n}")
    slug = factory.Sequence(lambda n: f"store-{n}")
