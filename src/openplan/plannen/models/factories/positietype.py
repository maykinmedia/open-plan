import uuid

import factory

from ..positietype import PositieType


class PositieTypeFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    naam = factory.Faker("sentence", nb_words=4)

    class Meta:
        model = PositieType
