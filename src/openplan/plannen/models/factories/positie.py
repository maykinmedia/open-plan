import uuid

import factory

from ..positie import Positie
from .positietype import PositieTypeFactory
from .subject import SubjectFactory


class PositieFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    subject = factory.SubFactory(SubjectFactory)
    positie_type = factory.SubFactory(PositieTypeFactory)

    class Meta:
        model = Positie
