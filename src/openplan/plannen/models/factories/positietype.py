import uuid

import factory
from factory.helpers import post_generation

from ..positietype import PositieType
from .configuratie import ConfiguratieFactory


class PositieTypeFactory(factory.django.DjangoModelFactory):
    uuid = factory.LazyFunction(uuid.uuid4)
    naam = factory.Faker("sentence", nb_words=4)

    class Meta:
        model = PositieType

    @post_generation
    def configuraties(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted is not None:
            self.configuraties.add(*extracted)
        else:
            self.configuraties.add(ConfiguratieFactory.create())
