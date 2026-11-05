import uuid

import factory

from ..positie import Positie
from .positietype import PositieTypeFactory
from .subject import SubjectFactory


class PositieFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    subject = factory.SubFactory(SubjectFactory)
    positietype = factory.SubFactory(PositieTypeFactory)
    domein = factory.LazyAttribute(
        lambda o: getattr(o.positietype.configuraties.first(), "domein", None)
    )

    class Meta:
        model = Positie
