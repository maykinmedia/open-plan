import uuid

from django.utils import timezone

import factory

from openplan.plannen.enums.status import PlanStatus

from ..plan import Plan


class PlanFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)

    naam = factory.Faker("sentence", nb_words=4)
    status = PlanStatus.ACTIEF
    startdatum = factory.LazyFunction(timezone.now)

    class Meta:
        model = Plan
