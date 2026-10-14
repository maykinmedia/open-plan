import uuid

import factory

from ..subject import Subject
from .plan import PlanFactory


class SubjectFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    plan = factory.SubFactory(PlanFactory)

    profiel = "urn:persoon:profiel:123"
    klant = "urn:klant:123"
    bsn = "123456789"

    class Meta:
        model = Subject
