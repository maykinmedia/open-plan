import uuid

from django.utils import timezone

import factory

from ..plan import Plan


class PlanFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    naam = factory.Faker("sentence", nb_words=4)
    startdatum = factory.LazyFunction(timezone.now)
    beoogde_startdatum = factory.LazyFunction(timezone.now)

    class Meta:
        model = Plan
