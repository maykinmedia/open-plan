import uuid

import factory

from ..subdoeltype import SubdoelType


class SubdoelTypeFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    naam = factory.Faker("sentence", nb_words=4)

    class Meta:
        model = SubdoelType
