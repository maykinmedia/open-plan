from django.core.exceptions import ValidationError
from django.test import TestCase

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
