from django.core.exceptions import ValidationError
from django.test import TestCase

from openplan.plannen.models.factories.doel import DoelFactory
from openplan.plannen.models.factories.doeltype import DoelTypeFactory
from openplan.plannen.models.factories.positie import PositieFactory
from openplan.plannen.models.factories.positietype import PositieTypeFactory


class DoelPositietypeTests(TestCase):
    def test_doeltype_that_allows_positietype_is_valid(self):
        positie = PositieFactory.create()
        doeltype = DoelTypeFactory.create(positietypen=[positie.positietype])
        doel = DoelFactory.build(positie=positie, doeltype=doeltype)

        doel.clean()

    def test_doeltype_that_does_not_allow_positietype_fails(self):
        positie = PositieFactory.create()
        doeltype = DoelTypeFactory.create(positietypen=[PositieTypeFactory.create()])
        doel = DoelFactory.build(positie=positie, doeltype=doeltype)

        with self.assertRaises(ValidationError) as cm:
            doel.clean()

        self.assertIn("positie", cm.exception.message_dict)

    def test_doeltype_without_positietypen_fails(self):
        positie = PositieFactory.create()
        doel = DoelFactory.build(positie=positie, doeltype=DoelTypeFactory.create())

        with self.assertRaises(ValidationError) as cm:
            doel.clean()

        self.assertIn("positie", cm.exception.message_dict)

    def test_missing_doeltype_is_skipped(self):
        doel = DoelFactory.build(positie=PositieFactory.create(), doeltype=None)

        doel.clean()
