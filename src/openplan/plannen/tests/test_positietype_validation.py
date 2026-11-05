from django.core.exceptions import ValidationError
from django.test import TestCase

from openplan.plannen.models.factories.configuratie import ConfiguratieFactory
from openplan.plannen.models.factories.domein import DomeinFactory
from openplan.plannen.models.factories.positie import PositieFactory
from openplan.plannen.models.factories.positietype import PositieTypeFactory


class PositieTypeDomeinTests(TestCase):
    def test_new_positietype_is_valid(self):
        positietype = PositieTypeFactory.build(domein=DomeinFactory.create())

        positietype.clean()

    def test_changing_domein_of_unused_positietype_is_valid(self):
        positietype = PositieTypeFactory.create()

        positietype.domein = DomeinFactory.create()

        positietype.clean()

    def test_changing_domein_of_used_positietype_fails(self):
        positietype = PositieFactory.create().positietype

        positietype.domein = DomeinFactory.create()

        with self.assertRaises(ValidationError) as cm:
            positietype.clean()

        self.assertIn("domein", cm.exception.message_dict)

    def test_other_changes_to_used_positietype_are_valid(self):
        positietype = PositieFactory.create().positietype

        positietype.naam = "Nieuwe naam"

        positietype.clean()


class PositieTypeConfiguratiesTests(TestCase):
    def test_configuraties_in_same_domein_are_valid(self):
        domein = DomeinFactory.create()
        positietype = PositieTypeFactory.create(domein=domein)
        configuraties = [
            ConfiguratieFactory.create(domein=domein),
            ConfiguratieFactory.create(domein=domein),
        ]

        positietype.controleer_configuraties(configuraties, domein)

    def test_configuratie_in_other_domein_fails(self):
        domein = DomeinFactory.create()
        positietype = PositieTypeFactory.create(domein=domein)
        configuraties = [
            ConfiguratieFactory.create(domein=domein),
            ConfiguratieFactory.create(domein=DomeinFactory.create()),
        ]

        with self.assertRaises(ValidationError) as cm:
            positietype.controleer_configuraties(configuraties, domein)

        self.assertIn("configuraties", cm.exception.message_dict)
