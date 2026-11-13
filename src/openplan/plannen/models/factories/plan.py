import uuid

from django.utils import timezone

import factory

from ..plan import Plan


class PlanFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    naam = factory.Sequence(lambda n: f"Plan {n}")
    startdatum = factory.LazyFunction(timezone.now)
    beoogde_startdatum = factory.LazyFunction(timezone.now)

    class Meta:
        model = Plan
