import uuid

from django.utils import timezone

import factory

from openplan.plannen.enums.status import PlanStatus

from ..doel import Doel
from .persoon import PersoonFactory


class DoelFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    persoon = factory.SubFactory(PersoonFactory)
    status = PlanStatus.ACTIEF
    titel = factory.Faker("sentence", nb_words=4)
    beschrijving = factory.Faker("paragraph", nb_sentences=3)
    startdatum = factory.LazyFunction(timezone.now)

    class Meta:
        model = Doel
