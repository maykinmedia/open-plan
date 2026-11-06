from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from openplan.plannen.models.factories.doel import DoelFactory
from openplan.plannen.models.factories.plan import PlanFactory
from openplan.plannen.models.factories.subdoel import SubdoelFactory
from openplan.plannen.models.positietype import PositieType
from openplan.plannen.models.validators import validate_positie_type_not_self

GELIJKE_DATUM_ERROR = (
    "2025-01-12 mag niet op een eerdere of dezelfde dag vallen als de 2025-01-12."
)
EERDERE_DATUM_ERROR = (
    "2024-01-12 mag niet op een eerdere of dezelfde dag vallen als de 2025-01-12."
)


class ValidatePositieTypeSelfTests(TestCase):
    def test_position_type_cannot_reference_itself(self):
        positie_type = PositieType(naam="Test")
        positie_type.doelpositie = positie_type

        with self.assertRaises(ValidationError) as context:
            validate_positie_type_not_self(positie_type)

        self.assertIn("doelpositie", context.exception.message_dict)

    def test_position_type_cannot_reference_its_descendant(self):
        grandparent = PositieType(naam="Grandparent")
        parent = PositieType(naam="Parent", doelpositie=grandparent)
        child = PositieType(naam="Child", doelpositie=parent)

        # Create a cycle: grandparent -> child -> parent -> grandparent
        grandparent.doelpositie = child

        with self.assertRaises(ValidationError) as context:
            validate_positie_type_not_self(grandparent)

        self.assertIn("doelpositie", context.exception.message_dict)

    def test_valid_parent_child_relationship(self):
        parent = PositieType(naam="Parent")
        child = PositieType(naam="Child", doelpositie=parent)

        self.assertIsNone(validate_positie_type_not_self(child))

    def test_position_type_without_target_is_valid(self):
        positie_type = PositieType(naam="Test", doelpositie=None)

        self.assertIsNone(validate_positie_type_not_self(positie_type))


class PlanTests(TestCase):
    def test_start_and_eind_datum_are_not_allowed_to_be_the_same(self):
        plan = PlanFactory.build(
            startdatum=date(2025, 1, 12),
            einddatum=date(2025, 1, 12),
        )

        with self.assertRaisesMessage(ValidationError, GELIJKE_DATUM_ERROR):
            plan.clean()

    def test_eind_datum_is_not_allowed_to_be_before_start_datum(self):
        plan = PlanFactory.build(
            startdatum=date(2025, 1, 12),
            einddatum=date(2024, 1, 12),
        )

        with self.assertRaisesMessage(ValidationError, EERDERE_DATUM_ERROR):
            plan.clean()

    def test_eind_datum_is_allowed_to_be_null(self):
        plan = PlanFactory.build(
            startdatum=date(2025, 1, 12),
            einddatum=None,
        )
        plan.clean()

    def test_beoogde_start_and_eind_datum_are_not_allowed_to_be_the_same(self):
        plan = PlanFactory.build(
            beoogde_startdatum=date(2025, 1, 12),
            beoogde_einddatum=date(2025, 1, 12),
        )

        with self.assertRaisesMessage(ValidationError, GELIJKE_DATUM_ERROR):
            plan.clean()

    def test_beoogde_eind_datum_is_not_allowed_to_be_before_beoogde_start_datum(self):
        plan = PlanFactory.build(
            beoogde_startdatum=date(2025, 1, 12),
            beoogde_einddatum=date(2024, 1, 12),
        )

        with self.assertRaisesMessage(ValidationError, EERDERE_DATUM_ERROR):
            plan.clean()

    def test_beoogde_eind_datum_is_allowed_to_be_null(self):
        plan = PlanFactory.build(
            beoogde_startdatum=date(2025, 1, 12),
            beoogde_einddatum=None,
        )
        plan.clean()


class DoelTests(TestCase):
    def test_start_and_eind_datum_are_not_allowed_to_be_the_same(self):
        doel = DoelFactory.build(
            startdatum=date(2025, 1, 12),
            einddatum=date(2025, 1, 12),
        )

        with self.assertRaisesMessage(ValidationError, GELIJKE_DATUM_ERROR):
            doel.clean()

    def test_eind_datum_is_not_allowed_to_be_before_start_datum(self):
        doel = DoelFactory.build(
            startdatum=date(2025, 1, 12),
            einddatum=date(2024, 1, 12),
        )

        with self.assertRaisesMessage(ValidationError, EERDERE_DATUM_ERROR):
            doel.clean()

    def test_eind_datum_is_allowed_to_be_null(self):
        doel = DoelFactory.build(
            startdatum=date(2025, 1, 12),
            einddatum=None,
        )
        doel.clean()

    def test_beoogde_start_and_eind_datum_are_not_allowed_to_be_the_same(self):
        doel = DoelFactory.build(
            beoogde_startdatum=date(2025, 1, 12),
            beoogde_einddatum=date(2025, 1, 12),
        )

        with self.assertRaisesMessage(ValidationError, GELIJKE_DATUM_ERROR):
            doel.clean()

    def test_beoogde_eind_datum_is_not_allowed_to_be_before_beoogde_start_datum(self):
        doel = DoelFactory.build(
            beoogde_startdatum=date(2025, 1, 12),
            beoogde_einddatum=date(2024, 1, 12),
        )

        with self.assertRaisesMessage(ValidationError, EERDERE_DATUM_ERROR):
            doel.clean()

    def test_beoogde_eind_datum_is_allowed_to_be_null(self):
        doel = DoelFactory.build(
            beoogde_startdatum=date(2025, 1, 12),
            beoogde_einddatum=None,
        )
        doel.clean()


class SubDoelTests(TestCase):
    def test_start_and_eind_datum_are_not_allowed_to_be_the_same(self):
        subdoel = SubdoelFactory.build(
            startdatum=date(2025, 1, 12),
            einddatum=date(2025, 1, 12),
        )

        with self.assertRaisesMessage(ValidationError, GELIJKE_DATUM_ERROR):
            subdoel.clean()

    def test_eind_datum_is_not_allowed_to_be_before_start_datum(self):
        subdoel = SubdoelFactory.build(
            startdatum=date(2025, 1, 12),
            einddatum=date(2024, 1, 12),
        )

        with self.assertRaisesMessage(ValidationError, EERDERE_DATUM_ERROR):
            subdoel.clean()

    def test_eind_datum_is_allowed_to_be_null(self):
        subdoel = SubdoelFactory.build(
            startdatum=date(2025, 1, 12),
            einddatum=None,
        )
        subdoel.clean()

    def test_beoogde_start_and_eind_datum_are_not_allowed_to_be_the_same(self):
        subdoel = SubdoelFactory.build(
            beoogde_startdatum=date(2025, 1, 12),
            beoogde_einddatum=date(2025, 1, 12),
        )

        with self.assertRaisesMessage(ValidationError, GELIJKE_DATUM_ERROR):
            subdoel.clean()

    def test_beoogde_eind_datum_is_not_allowed_to_be_before_beoogde_start_datum(self):
        subdoel = SubdoelFactory.build(
            beoogde_startdatum=date(2025, 1, 12),
            beoogde_einddatum=date(2024, 1, 12),
        )

        with self.assertRaisesMessage(ValidationError, EERDERE_DATUM_ERROR):
            subdoel.clean()

    def test_beoogde_eind_datum_is_allowed_to_be_null(self):
        subdoel = SubdoelFactory.build(
            beoogde_startdatum=date(2025, 1, 12),
            beoogde_einddatum=None,
        )
        subdoel.clean()
