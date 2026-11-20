from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from openplan.utils.fields import UuidURNField


class UuidURNFieldTests(SimpleTestCase):
    def test_valid_urn_with_uuid(self):
        field = UuidURNField()
        field.run_validators(
            "urn:nld:gemeente:product:uuid:2f463a72-83fd-48bc-a3cf-901755c1644c"
        )

    def test_urn_without_uuid(self):
        field = UuidURNField()
        with self.assertRaises(ValidationError) as cm:
            field.run_validators("urn:nld:gemeente:product:12345")
        self.assertEqual(cm.exception.error_list[0].code, "urn_without_uuid")

    def test_invalid_urn(self):
        field = UuidURNField()
        with self.assertRaises(ValidationError):
            field.run_validators("geen-geldige-urn")
