from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from openplan.plannen.models import (
    Configuratie,
    Domein,
    Plan,
    Positie,
    PositieType,
    Subject,
)


class PositieDomeinTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.werk = Domein.objects.create(naam="Werk")
        cls.inkomen = Domein.objects.create(naam="Inkomen")

        werk_configuratie = Configuratie.objects.create(domein=cls.werk)
        inkomen_configuratie = Configuratie.objects.create(domein=cls.inkomen)

        cls.werk_type_a = PositieType.objects.create(
            naam="Nog niet beschikbaar", configuratie=werk_configuratie
        )
        cls.werk_type_b = PositieType.objects.create(
            naam="Meedoen voor stabiliteit", configuratie=werk_configuratie
        )
        cls.inkomen_type = PositieType.objects.create(
            naam="Inkomen", configuratie=inkomen_configuratie
        )

        cls.subject = Subject.objects.create(plan=Plan.objects.create())

    def test_domain_is_derived_from_position_type(self):
        positie = Positie.objects.create(
            subject=self.subject, positietype=self.werk_type_a
        )

        self.assertEqual(positie.domein, self.werk)

    def test_given_domain_is_overwritten_by_derived_domain(self):
        positie = Positie(
            subject=self.subject, positietype=self.werk_type_a, domein=self.inkomen
        )
        positie.save()

        self.assertEqual(positie.domein, self.werk)

    def test_second_position_in_same_domain_fails_on_database(self):
        Positie.objects.create(subject=self.subject, positietype=self.werk_type_a)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Positie.objects.create(subject=self.subject, positietype=self.werk_type_b)

    def test_second_position_in_same_domain_fails_in_full_clean(self):
        Positie.objects.create(subject=self.subject, positietype=self.werk_type_a)
        positie = Positie(subject=self.subject, positietype=self.werk_type_b)

        with self.assertRaises(ValidationError):
            positie.full_clean()

    def test_position_in_other_domain_is_valid(self):
        Positie.objects.create(subject=self.subject, positietype=self.werk_type_a)
        Positie.objects.create(subject=self.subject, positietype=self.inkomen_type)

        self.assertEqual(self.subject.posities.count(), 2)

    def test_other_subject_in_same_domain_is_valid(self):
        other_subject = Subject.objects.create(plan=Plan.objects.create())
        Positie.objects.create(subject=self.subject, positietype=self.werk_type_a)
        Positie.objects.create(subject=other_subject, positietype=self.werk_type_a)

        self.assertEqual(Positie.objects.filter(domein=self.werk).count(), 2)

    def test_changing_type_within_same_domain_is_valid(self):
        positie = Positie.objects.create(
            subject=self.subject, positietype=self.werk_type_a
        )

        positie.positietype = self.werk_type_b
        positie.save()

        positie.refresh_from_db()
        self.assertEqual(positie.positietype, self.werk_type_b)
        self.assertEqual(positie.domein, self.werk)

    def test_changing_type_to_other_domain_fails_on_save(self):
        positie = Positie.objects.create(
            subject=self.subject, positietype=self.werk_type_a
        )

        positie.positietype = self.inkomen_type

        with self.assertRaises(ValidationError) as context:
            positie.save()

        self.assertIn("positietype", context.exception.message_dict)

        positie.refresh_from_db()
        self.assertEqual(positie.positietype, self.werk_type_a)
        self.assertEqual(positie.domein, self.werk)

    def test_changing_type_to_other_domain_fails_in_full_clean(self):
        positie = Positie.objects.create(
            subject=self.subject, positietype=self.werk_type_a
        )

        positie.positietype = self.inkomen_type

        with self.assertRaises(ValidationError) as context:
            positie.full_clean()

        self.assertIn("positietype", context.exception.message_dict)

    def test_existing_position_is_not_seen_as_duplicate(self):
        positie = Positie.objects.create(
            subject=self.subject, positietype=self.werk_type_a
        )

        self.assertIsNone(positie.full_clean())
