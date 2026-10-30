import factory

from ..configuratie import Configuratie
from .domein import DomeinFactory


class ConfiguratieFactory(factory.django.DjangoModelFactory):
    domein = factory.SubFactory(DomeinFactory)
    naam = factory.Sequence(lambda n: f"Configuratie {n}")
    omschrijving = factory.Faker("paragraph", nb_sentences=3)
    status = "actief"

    class Meta:
        model = Configuratie
