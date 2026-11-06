import uuid

from django.utils import timezone

import factory

from openplan.plannen.enums.status import Status

from ..subdoel import SubDoel
from .doel import DoelFactory


class SubdoelFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    doel = factory.SubFactory(DoelFactory)
    status = Status.ACTIEF
    naam = factory.Faker("sentence", nb_words=4)
    omschrijving = factory.Faker("paragraph", nb_sentences=3)
    startdatum = factory.LazyFunction(timezone.now)
    beoogde_startdatum = factory.LazyFunction(timezone.now)

    class Meta:
        model = SubDoel
