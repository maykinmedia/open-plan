from django.core.exceptions import ValidationError
from django.test import TestCase

from openplan.plannen.models import Doel, Subdoel
from openplan.plannen.models.factories.doel import DoelFactory
from openplan.plannen.models.factories.doeltype import DoelTypeFactory
from openplan.plannen.models.factories.subdoel import SubdoelFactory
from openplan.plannen.models.factories.subdoeltype import SubdoelTypeFactory
from openplan.plannen.models.positietype import PositieType
from openplan.plannen.models.validators import validate_positie_type_not_self


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
