import uuid

from django.utils import timezone

import factory

from openplan.plannen.enums.status import PlanStatus

from ..doel import Doel
from .doeltype import DoelTypeFactory
from .plan import PlanFactory
from .subject import SubjectFactory


class DoelFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    doeltype = factory.SubFactory(DoelTypeFactory)
    persoon = factory.SubFactory(SubjectFactory)
    status = PlanStatus.ACTIEF
    titel = factory.Faker("sentence", nb_words=4)
    beschrijving = factory.Faker("paragraph", nb_sentences=3)
    startdatum = factory.LazyFunction(timezone.now)

    hoofd_doel = None

    class Meta:
        model = Doel

    @factory.post_generation
    def plannen(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for plan in extracted:
                self.plannen.add(plan)
        else:
            self.plannen.add(PlanFactory.create())
