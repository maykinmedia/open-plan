from django.utils import timezone

import factory

from openplan.plannen.models.evaluatie import Evaluatie
from openplan.plannen.models.evaluatietype import Evaluatietype

from .plan import PlanFactory


class EvaluatieTypeFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"EvaluatieType {n}")
    omschrijving = factory.Sequence(lambda n: f"Beschrijving voor EvaluatieType {n}")

    class Meta:
        model = Evaluatietype


class EvaluatieFactory(factory.django.DjangoModelFactory):
    plan = factory.SubFactory(PlanFactory)
    evaluatietype = factory.SubFactory(EvaluatieTypeFactory)
    naam = factory.Sequence(lambda n: f"Evaluatie {n}")
    datum = factory.LazyFunction(timezone.now)

    class Meta:
        model = Evaluatie
