from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from openplan.plannen.models.factories.configuratie import ConfiguratieFactory
from openplan.plannen.models.factories.domein import DomeinFactory
from openplan.plannen.models.factories.plan import PlanFactory
from openplan.plannen.models.factories.positie import PositieFactory
from openplan.plannen.models.factories.positietype import PositieTypeFactory
from openplan.plannen.models.factories.subject import SubjectFactory


class PositieDomeinTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.werk = DomeinFactory(naam="Werk")
        cls.inkomen = DomeinFactory(naam="Inkomen")

        werk_configuratie = ConfiguratieFactory(domein=cls.werk)
        inkomen_configuratie = ConfiguratieFactory(domein=cls.inkomen)

        cls.werk_type_a = PositieTypeFactory(
            naam="Nog niet beschikbaar", configuraties=[werk_configuratie]
        )
        cls.werk_type_b = PositieTypeFactory(
            naam="Meedoen voor stabiliteit", configuraties=[werk_configuratie]
        )
        cls.inkomen_type = PositieTypeFactory(
            naam="Inkomen", configuraties=[inkomen_configuratie]
        )

        cls.subject = SubjectFactory(plan=PlanFactory.create())

    def test_positietype_without_configuratie_fails(self):
        positie = PositieFactory.build(
            subject=self.subject, positietype=PositieTypeFactory(configuraties=[])
        )

        with self.assertRaises(ValidationError) as cm:
            positie.clean()

        self.assertIn("positietype", cm.exception.message_dict)

    def test_second_positie_in_same_domein_fail(self):
        PositieFactory.create(subject=self.subject, positietype=self.werk_type_a)
        positie = PositieFactory.build(
            subject=self.subject, positietype=self.werk_type_b
        )

        with self.assertRaises(ValidationError) as cm:
            positie.clean()

        self.assertIn("subject", cm.exception.message_dict)

    def test_moving_positie_to_subject_with_positie_in_domein_fails(self):
        PositieFactory.create(subject=self.subject, positietype=self.werk_type_a)
        positie = PositieFactory.create(positietype=self.werk_type_b)

        positie.subject = self.subject

        with self.assertRaises(ValidationError) as cm:
            positie.clean()

        self.assertIn("subject", cm.exception.message_dict)

    def test_second_positie_in_same_domein_fails(self):
        PositieFactory.create(subject=self.subject, positietype=self.werk_type_a)

        with self.assertRaises(IntegrityError), transaction.atomic():
            PositieFactory.create(subject=self.subject, positietype=self.werk_type_b)

        self.assertEqual(self.subject.posities.count(), 1)

    def test_positie_in_other_domein_is_valid(self):
        PositieFactory.create(subject=self.subject, positietype=self.werk_type_a)
        positie = PositieFactory.build(
            subject=self.subject, positietype=self.inkomen_type
        )

        positie.clean()

    def test_other_subject_in_same_domein_is_valid(self):
        PositieFactory.create(subject=self.subject, positietype=self.werk_type_a)
        positie = PositieFactory.build(
            subject=SubjectFactory(plan=PlanFactory.create()),
            positietype=self.werk_type_a,
        )

        positie.clean()

    def test_existing_positie_is_not_seen_as_duplicate(self):
        positie = PositieFactory.create(
            subject=self.subject, positietype=self.werk_type_a
        )

        positie.clean()

    def test_changing_positietype_within_same_domein_is_valid(self):
        positie = PositieFactory.create(
            subject=self.subject, positietype=self.werk_type_a
        )

        positie.positietype = self.werk_type_b
        positie.clean()

        self.assertEqual(positie.domein, self.werk)

    def test_changing_positietype_to_other_domein_fails(self):
        positie = PositieFactory.create(
            subject=self.subject, positietype=self.werk_type_a
        )

        positie.positietype = self.inkomen_type

        with self.assertRaises(ValidationError) as cm:
            positie.clean()

        self.assertIn("positietype", cm.exception.message_dict)

    def test_changing_domein_fails(self):
        positie = PositieFactory.create(
            subject=self.subject, positietype=self.werk_type_a
        )

        positie.domein = self.inkomen

        with self.assertRaises(ValidationError) as cm:
            positie.clean()

        self.assertIn("domein", cm.exception.message_dict)
