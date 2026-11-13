import uuid

import factory

from ..subdoeltype import SubdoelType


class SubdoelTypeFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    naam = factory.Sequence(lambda n: f"SubdoelType {n}")

    class Meta:
        model = SubdoelType
