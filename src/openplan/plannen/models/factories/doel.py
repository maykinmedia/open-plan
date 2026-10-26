import uuid

from django.utils import timezone

import factory

from openplan.plannen.enums.status import Status

from ..doel import Doel
from .doeltype import DoelTypeFactory
from .positie import PositieFactory


class DoelFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    doeltype = factory.SubFactory(DoelTypeFactory)
    positie = factory.SubFactory(PositieFactory)
    status = Status.ACTIEF
    naam = factory.Faker("sentence", nb_words=4)
    omschrijving = factory.Faker("paragraph", nb_sentences=3)
    startdatum = factory.LazyFunction(timezone.now)

    class Meta:
        model = Doel
