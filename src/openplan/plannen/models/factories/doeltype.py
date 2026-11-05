import uuid

import factory
from factory.helpers import post_generation

from openplan.plannen.enums.doel import DoelTypeEnum

from ..doeltype import DoelType


class DoelTypeFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    doel_type = factory.Iterator([choice[0] for choice in DoelTypeEnum.choices])

    class Meta:
        model = DoelType

    @post_generation
    def positietypen(self, create, extracted, **kwargs):
        if create and extracted:
            self.positietypen.add(*extracted)
