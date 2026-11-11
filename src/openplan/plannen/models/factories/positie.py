import uuid

import factory

from ..positie import Positie
from .positietype import PositieTypeFactory
from .subject import SubjectFactory


class PositieFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    subject = factory.SubFactory(SubjectFactory)
    positietype = factory.SubFactory(PositieTypeFactory)
    naam = factory.Sequence(lambda n: f"Positie {n}")

    class Meta:
        model = Positie
