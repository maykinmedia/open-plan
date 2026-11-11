import uuid

from django.utils import timezone

import factory

from ..subdoel import Subdoel
from .doel import DoelFactory
from .subdoeltype import SubdoelTypeFactory


class SubdoelFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    subdoeltype = factory.SubFactory(SubdoelTypeFactory)
    doel = factory.SubFactory(DoelFactory)
    naam = factory.Faker("sentence", nb_words=4)
    omschrijving = factory.Faker("paragraph", nb_sentences=3)
    startdatum = factory.LazyFunction(timezone.now)
    beoogde_startdatum = factory.LazyFunction(timezone.now)

    class Meta:
        model = Subdoel
