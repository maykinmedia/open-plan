import uuid

from django.utils import timezone

import factory

from openplan.plannen.models.evaluatie import Evaluatie
from openplan.plannen.models.evaluatietype import EvaluatieType

from .plan import PlanFactory


class EvaluatieTypeFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    naam = factory.Sequence(lambda n: f"EvaluatieType {n}")
    omschrijving = factory.Sequence(lambda n: f"Beschrijving voor EvaluatieType {n}")

    class Meta:
        model = EvaluatieType


class EvaluatieFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    plan = factory.SubFactory(PlanFactory)
    evaluatie_type = factory.SubFactory(EvaluatieTypeFactory)
    datum = factory.LazyFunction(timezone.now)

    class Meta:
        model = Evaluatie
