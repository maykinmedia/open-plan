from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from openplan.plannen.models.factories.doel import DoelFactory
from openplan.plannen.models.factories.plan import PlanFactory
from openplan.plannen.models.factories.subdoel import SubdoelFactory
from openplan.plannen.models import Doel, Subdoel
from openplan.plannen.models.factories.doel import DoelFactory
from openplan.plannen.models.factories.doeltype import DoelTypeFactory
from openplan.plannen.models.factories.subdoel import SubdoelFactory
from openplan.plannen.models.factories.subdoeltype import SubdoelTypeFactory
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


class DoelModelTests(TestCase):
    def test_changing_doeltype_raises_and_does_not_write(self):
        doel = DoelFactory.create()
        original_doeltype_id = doel.doeltype_id

        doel.doeltype = DoelTypeFactory.create()

        with self.assertRaises(ValidationError) as cm:
            doel.save()

        self.assertIn("doeltype", cm.exception.message_dict)
        self.assertEqual(Doel.objects.get(pk=doel.pk).doeltype_id, original_doeltype_id)

    def test_saving_other_changes_is_allowed(self):
        doel = DoelFactory.create()
        original_doeltype_id = doel.doeltype_id

        doel.naam = "Nieuwe naam"
        doel.save()

        doel.refresh_from_db()
        self.assertEqual(doel.naam, "Nieuwe naam")
        self.assertEqual(doel.doeltype_id, original_doeltype_id)


class SubdoelModelTests(TestCase):
    def test_changing_subdoeltype_raises_and_does_not_write(self):
        subdoel = SubdoelFactory.create()
        original_subdoeltype_id = subdoel.subdoeltype_id

        subdoel.subdoeltype = SubdoelTypeFactory.create()

        with self.assertRaises(ValidationError) as cm:
            subdoel.save()

        self.assertIn("subdoeltype", cm.exception.message_dict)
        self.assertEqual(
            Subdoel.objects.get(pk=subdoel.pk).subdoeltype_id, original_subdoeltype_id
        )

    def test_saving_other_changes_is_allowed(self):
        subdoel = SubdoelFactory.create()
        original_subdoeltype_id = subdoel.subdoeltype_id

        subdoel.naam = "Nieuwe naam"
        subdoel.save()

        subdoel.refresh_from_db()
        self.assertEqual(subdoel.naam, "Nieuwe naam")
        self.assertEqual(subdoel.subdoeltype_id, original_subdoeltype_id)
