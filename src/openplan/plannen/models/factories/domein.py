import factory

from openplan.plannen.models.domein import Domein


class DomeinFactory(factory.django.DjangoModelFactory):
    naam = factory.Sequence(lambda n: f"Domein {n}")
    omschrijving = factory.Faker("text", locale="nl_NL")
    status = "actief"

    class Meta:
        model = Domein
