import uuid

import factory

from ..positietype import PositieType


class PositieTypeFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    naam = factory.Sequence(lambda n: f"PositieType {n}")

    class Meta:
        model = PositieType
