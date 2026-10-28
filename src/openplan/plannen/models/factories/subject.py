import uuid

import factory

from openplan.plannen.enums.status import SubjectType

from ..subject import Subject
from .plan import PlanFactory


class SubjectFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    plan = factory.SubFactory(PlanFactory)
    subjecttype = SubjectType.PERSOON
    profiel = "urn:persoon:profiel:123"
    klant = "urn:klant:123"
    bsn = "123456789"

    class Meta:
        model = Subject
