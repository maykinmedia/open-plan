import uuid

import factory

from ..evaluatietype import Evaluatietype


class EvaluatietypeFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    naam = factory.Sequence(lambda n: f"SubdoelType {n}")

    class Meta:
        model = Evaluatietype
