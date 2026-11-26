from datetime import date

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.test import APIClient
from vng_api_common.tests import get_validation_errors

from openplan.plannen.enums.status import Doelstatus
from openplan.plannen.models.factories.doel import DoelFactory
from openplan.plannen.models.factories.subdoel import SubdoelFactory
from openplan.plannen.models.factories.subdoeltype import SubdoelTypeFactory

from ...models.subdoel import Subdoel
from .api_testcase import APITestCase


class SubdoelAPITests(APITestCase):
    DATUM_ERROR = _(
        "De einddatum mag niet op een eerdere of dezelfde dag vallen als de startdatum."
    )
    BEOOGDE_EINDDATUM_ERROR = _(
        "De beoogde_einddatum mag niet op een eerdere of dezelfde dag vallen "
        "als de beoogde_startdatum."
    )

    def setUp(self):
        super().setUp()
        self.subdoeltype = SubdoelTypeFactory.create()
        self.doel = DoelFactory.create()

        self.data = {
            "subdoeltypeUuid": str(self.subdoeltype.uuid),
            "doelUuid": str(self.doel.uuid),
            "naam": "Test Subdoel",
            "startdatum": str(date.today()),
            "beoogde_startdatum": date.today().isoformat(),
            "omschrijving": "Beschrijving test",
        }

    def test_create_subdoel(self):
        url = reverse("plannen:subdoel-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        subdoel = Subdoel.objects.get(uuid=response.data["uuid"])
        self.assertEqual(subdoel.naam, "Test Subdoel")
        self.assertEqual(subdoel.doel, self.doel)
        self.assertEqual(subdoel.subdoeltype, self.subdoeltype)

    def test_list_subdoelen(self):
        SubdoelFactory.create_batch(3, doel=self.doel)

        url = reverse("plannen:subdoel-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 3)

        for subdoel_data in data:
            self.assertIn("uuid", subdoel_data)

    def test_retrieve_subdoel(self):
        subdoel = SubdoelFactory.create()

        url = reverse("plannen:subdoel-detail", kwargs={"uuid": subdoel.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(subdoel.uuid))

    def test_update_subdoel(self):
        subdoel = SubdoelFactory.create()
        url = reverse("plannen:subdoel-detail", kwargs={"uuid": subdoel.uuid})
        data = {
            "doelUuid": str(subdoel.doel.uuid),
            "naam": "Test update Subdoel",
            "startdatum": str(date.today()),
            "beoogde_startdatum": date.today().isoformat(),
            "omschrijving": "Beschrijving update test",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        subdoel.refresh_from_db()
        self.assertEqual(subdoel.naam, "Test update Subdoel")

    def test_update_subdoel_without_subdoeltype_is_allowed(self):
        subdoel = SubdoelFactory.create()
        original_subdoeltype = subdoel.subdoeltype

        url = reverse("plannen:subdoel-detail", kwargs={"uuid": subdoel.uuid})
        data = {
            "doelUuid": str(subdoel.doel.uuid),
            "naam": "Zonder subdoeltype",
            "startdatum": str(date.today()),
            "beoogde_startdatum": date.today().isoformat(),
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        subdoel.refresh_from_db()
        self.assertEqual(subdoel.subdoeltype, original_subdoeltype)

    def test_partial_update_subdoel(self):
        subdoel = SubdoelFactory.create()

        url = reverse("plannen:subdoel-detail", kwargs={"uuid": subdoel.uuid})
        response = self.client.patch(url, {"naam": "Nieuwe naam"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subdoel.refresh_from_db()
        self.assertEqual(subdoel.naam, "Nieuwe naam")

    def test_patch_subdoeltype_returns_400_and_does_not_write(self):
        subdoel = SubdoelFactory.create(naam="Origineel")
        original_subdoeltype = subdoel.subdoeltype

        url = reverse("plannen:subdoel-detail", kwargs={"uuid": subdoel.uuid})
        data = {
            "subdoeltypeUuid": str(SubdoelTypeFactory.create().uuid),
            "naam": "Gewijzigd",
        }

        response = self.client.patch(url, data, format="json")

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.json()
        )
        invalid_params = response.json()["invalidParams"]
        self.assertEqual(len(invalid_params), 1)
        self.assertEqual(invalid_params[0]["name"], "subdoeltypeUuid")

        subdoel.refresh_from_db()
        self.assertEqual(subdoel.subdoeltype, original_subdoeltype)
        self.assertEqual(subdoel.naam, "Origineel")

    def test_delete_subdoel(self):
        subdoel = SubdoelFactory.create()

        url = reverse("plannen:subdoel-detail", kwargs={"uuid": subdoel.uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subdoel.objects.filter(uuid=subdoel.uuid).exists())

    def test_create_subdoel_returns_nested_doel_and_subdoeltype(self):
        url = reverse("plannen:subdoel-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        data = response.json()
        self.assertEqual(data["doel"]["uuid"], str(self.doel.uuid))
        self.assertEqual(data["doel"]["naam"], self.doel.naam)
        self.assertEqual(data["subdoeltype"]["uuid"], str(self.subdoeltype.uuid))
        self.assertNotIn("doelUuid", data)
        self.assertNotIn("subdoeltypeUuid", data)

    def test_create_subdoel_without_doel(self):
        url = reverse("plannen:subdoel-list")
        data = {**self.data}
        del data["doelUuid"]
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "doelUuid")
        self.assertEqual(error["code"], "required")
        self.assertFalse(Subdoel.objects.exists())

    def test_create_subdoel_unknown_doel(self):
        url = reverse("plannen:subdoel-list")
        data = {**self.data, "doelUuid": "00000000-0000-4000-8000-000000000000"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "doelUuid")
        self.assertEqual(error["code"], "does_not_exist")
        self.assertFalse(Subdoel.objects.exists())

    def test_create_subdoel_without_subdoeltype(self):
        url = reverse("plannen:subdoel-list")
        data = {**self.data}
        del data["subdoeltypeUuid"]
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "subdoeltypeUuid")
        self.assertEqual(error["code"], "required")
        self.assertFalse(Subdoel.objects.exists())

    def test_create_subdoel_unknown_subdoeltype(self):
        url = reverse("plannen:subdoel-list")
        data = {
            **self.data,
            "subdoeltypeUuid": "00000000-0000-4000-8000-000000000000",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "subdoeltypeUuid")
        self.assertEqual(error["code"], "does_not_exist")
        self.assertFalse(Subdoel.objects.exists())

    def test_retrieve_subdoel_includes_doel(self):
        subdoel = SubdoelFactory.create(doel=self.doel)

        url = reverse("plannen:subdoel-detail", kwargs={"uuid": subdoel.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["doel"]["uuid"], str(self.doel.uuid))

    def test_update_subdoel_without_doel(self):
        subdoel = SubdoelFactory.create(doel=self.doel)
        url = reverse("plannen:subdoel-detail", kwargs={"uuid": subdoel.uuid})
        data = {
            "naam": "Test update Subdoel",
            "startdatum": str(date.today()),
            "beoogde_startdatum": date.today().isoformat(),
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "doelUuid")
        self.assertEqual(error["code"], "required")
        subdoel.refresh_from_db()
        self.assertEqual(subdoel.doel, self.doel)

    def test_partial_update_doel(self):
        subdoel = SubdoelFactory.create(doel=self.doel)
        nieuw_doel = DoelFactory.create()

        url = reverse("plannen:subdoel-detail", kwargs={"uuid": subdoel.uuid})
        response = self.client.patch(
            url, {"doelUuid": str(nieuw_doel.uuid)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(response.json()["doel"]["uuid"], str(nieuw_doel.uuid))
        subdoel.refresh_from_db()
        self.assertEqual(subdoel.doel, nieuw_doel)

    def test_create_subdoel_with_valid_einddatums(self):
        url = reverse("plannen:subdoel-list")
        data = {
            **self.data,
            "startdatum": "2026-01-10",
            "einddatum": "2026-01-20",
            "beoogde_startdatum": "2026-01-10",
            "beoogde_einddatum": "2026-01-20",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

    def test_create_subdoel_einddatum_before_startdatum(self):
        url = reverse("plannen:subdoel-list")
        data = {**self.data, "startdatum": "2026-01-10", "einddatum": "2026-01-05"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "einddatum")
        self.assertEqual(error["reason"], self.DATUM_ERROR)
        self.assertFalse(Subdoel.objects.exists())

    def test_create_subdoel_einddatum_same_as_startdatum(self):
        url = reverse("plannen:subdoel-list")
        data = {**self.data, "startdatum": "2026-01-10", "einddatum": "2026-01-10"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "einddatum")
        self.assertEqual(error["reason"], self.DATUM_ERROR)

    def test_create_subdoel_beoogde_einddatum_before_beoogde_startdatum(self):
        url = reverse("plannen:subdoel-list")
        data = {
            **self.data,
            "beoogde_startdatum": "2026-01-10",
            "beoogde_einddatum": "2026-01-05",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "beoogdeEinddatum")
        self.assertEqual(error["reason"], self.BEOOGDE_EINDDATUM_ERROR)
        self.assertFalse(Subdoel.objects.exists())

    def test_partial_update_einddatum_before_existing_startdatum(self):
        subdoel = SubdoelFactory.create(startdatum=date(2026, 1, 10), einddatum=None)

        url = reverse("plannen:subdoel-detail", kwargs={"uuid": subdoel.uuid})
        response = self.client.patch(url, {"einddatum": "2026-01-05"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "einddatum")
        self.assertEqual(error["reason"], self.DATUM_ERROR)
        subdoel.refresh_from_db()
        self.assertIsNone(subdoel.einddatum)

    def test_partial_update_startdatum_after_existing_einddatum(self):
        subdoel = SubdoelFactory.create(
            startdatum=date(2026, 1, 10), einddatum=date(2026, 1, 20)
        )

        url = reverse("plannen:subdoel-detail", kwargs={"uuid": subdoel.uuid})
        response = self.client.patch(url, {"startdatum": "2026-01-25"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "einddatum")
        self.assertEqual(error["reason"], self.DATUM_ERROR)
        subdoel.refresh_from_db()
        self.assertEqual(subdoel.startdatum, date(2026, 1, 10))

    def test_partial_update_valid_einddatum(self):
        subdoel = SubdoelFactory.create(startdatum=date(2026, 1, 10), einddatum=None)

        url = reverse("plannen:subdoel-detail", kwargs={"uuid": subdoel.uuid})
        response = self.client.patch(url, {"einddatum": "2026-01-20"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subdoel.refresh_from_db()
        self.assertEqual(subdoel.einddatum, date(2026, 1, 20))

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:subdoel-list")

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_doel_uuid(self):
        subdoel = SubdoelFactory(doel=self.doel)
        SubdoelFactory(doel=DoelFactory.create())

        url = reverse("plannen:subdoel-list")
        response = self.client.get(url, {"doel__uuid": str(self.doel.uuid)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(subdoel.uuid))

    def test_filter_status(self):
        subdoel1 = SubdoelFactory(status=Doelstatus.GEPLAND)
        SubdoelFactory(status=Doelstatus.GESTART)

        url = reverse("plannen:subdoel-list")
        response = self.client.get(url, {"status": Doelstatus.GEPLAND})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(subdoel1.uuid))

    def test_filter_naam(self):
        subdoel1 = SubdoelFactory(naam="taalcursus")
        SubdoelFactory(naam="Rijden")

        url = reverse("plannen:subdoel-list")

        with self.subTest("exact"):
            response = self.client.get(url, {"naam": "taalcursus"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["uuid"], str(subdoel1.uuid))

        with self.subTest("icontains"):
            response = self.client.get(url, {"naam__icontains": "TAAL"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["uuid"], str(subdoel1.uuid))

    def test_filter_omschrijving_icontains(self):
        subdoel1 = SubdoelFactory(omschrijving="Leren fietsen in de stad")
        SubdoelFactory(omschrijving="Iets anders")

        url = reverse("plannen:subdoel-list")
        response = self.client.get(url, {"omschrijving__icontains": "fietsen"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(subdoel1.uuid))

    def _assert_date_filter(self, field, start, eind):
        """Shared exact/lte/gte checks for a date field filter."""
        url = reverse("plannen:subdoel-list")
        first = SubdoelFactory(**start)
        SubdoelFactory(**eind)

        with self.subTest(f"{field} exact"):
            response = self.client.get(url, {field: start[field].isoformat()})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["uuid"], str(first.uuid))

        with self.subTest(f"{field} lte"):
            response = self.client.get(url, {f"{field}__lte": start[field].isoformat()})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest(f"{field} gte"):
            response = self.client.get(url, {f"{field}__gte": eind[field].isoformat()})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    def test_startdatum_filter(self):
        self._assert_date_filter(
            "startdatum",
            {"startdatum": date(2026, 1, 1)},
            {"startdatum": date(2026, 2, 1)},
        )

    def test_einddatum_filter(self):
        self._assert_date_filter(
            "einddatum",
            {"startdatum": date(2026, 1, 1), "einddatum": date(2026, 1, 15)},
            {"startdatum": date(2026, 2, 1), "einddatum": date(2026, 2, 15)},
        )

    def test_beoogde_startdatum_filter(self):
        self._assert_date_filter(
            "beoogde_startdatum",
            {"beoogde_startdatum": date(2026, 1, 1)},
            {"beoogde_startdatum": date(2026, 2, 1)},
        )

    def test_beoogde_einddatum_filter(self):
        self._assert_date_filter(
            "beoogde_einddatum",
            {
                "beoogde_startdatum": date(2026, 1, 1),
                "beoogde_einddatum": date(2026, 1, 15),
            },
            {
                "beoogde_startdatum": date(2026, 2, 1),
                "beoogde_einddatum": date(2026, 2, 15),
            },
        )
