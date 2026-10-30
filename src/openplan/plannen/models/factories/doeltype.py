import uuid

import factory

from ..doeltype import DoelType


class DoelTypeFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    naam = factory.Faker("sentence", nb_words=4)

    class Meta:
        model = DoelType
