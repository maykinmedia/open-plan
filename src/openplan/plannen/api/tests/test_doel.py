from datetime import date, datetime
from unittest.mock import MagicMock, patch

from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.test import APIClient
from vng_api_common.tests import get_validation_errors

from openplan.plannen.enums.status import Resultaat, Status
from openplan.plannen.models.factories.doel import DoelFactory
from openplan.plannen.models.factories.doeltype import DoelTypeFactory
from openplan.plannen.models.factories.positie import PositieFactory

from ...metrics import (
    doelen_create_counter,
    doelen_delete_counter,
    doelen_update_counter,
)
from ...models.doel import Doel
from .api_testcase import APITestCase


class DoelAPITests(APITestCase):
    DATUM_ERROR = _(
        "De einddatum mag niet op een eerdere of dezelfde dag vallen als de startdatum."
    )
    BEOOGDE_EINDDATUM_ERROR = _(
        "De beoogde_einddatum mag niet op een eerdere of dezelfde dag vallen "
        "als de beoogde_startdatum."
    )

    def setUp(self):
        super().setUp()
        self.hoofddoel_type = DoelTypeFactory.create(naam="hoofddoel")
        self.positie = PositieFactory.create()

        self.data = {
            "doeltypeUuid": str(self.hoofddoel_type.uuid),
            "positieUuid": str(self.positie.uuid),
            "naam": "Test Doel",
            "startdatum": str(date.today()),
            "beoogde_startdatum": date.today().isoformat(),
            "omschrijving": "Beschrijving test",
        }

    def test_create_doel(self):
        url = reverse("plannen:doel-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        doel = Doel.objects.get(uuid=response.data["uuid"])
        self.assertEqual(doel.naam, "Test Doel")

    def test_list_doelens(self):
        DoelFactory.create_batch(3, positie=self.positie)

        url = reverse("plannen:doel-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 3)

        for doel_data in data:
            self.assertIn("uuid", doel_data)

    def test_retrieve_doel(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(doel.uuid))

    def test_update_doel(self):
        doel = DoelFactory.create()
        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        data = {
            "positieUuid": str(doel.positie.uuid),
            "naam": "Test update Doel",
            "startdatum": str(date.today()),
            "beoogde_startdatum": date.today().isoformat(),
            "omschrijving": "Beschrijving update test",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doel.refresh_from_db()
        self.assertEqual(doel.naam, "Test update Doel")

    def test_partial_update_doel(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        data = {"naam": "New titel"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doel.refresh_from_db()

    def test_patch_doeltype_returns_400_and_does_not_write(self):
        doel = DoelFactory.create(naam="Origineel")
        original_doeltype = doel.doeltype

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        data = {
            "doeltypeUuid": str(DoelTypeFactory.create().uuid),
            "naam": "Gewijzigd",
        }

        response = self.client.patch(url, data, format="json")

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.json()
        )
        invalid_params = response.json()["invalidParams"]
        self.assertEqual(len(invalid_params), 1)
        self.assertEqual(invalid_params[0]["name"], "doeltypeUuid")

        doel.refresh_from_db()
        self.assertEqual(doel.doeltype, original_doeltype)
        self.assertEqual(doel.naam, "Origineel")

    def test_delete_doel(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doel.objects.filter(uuid=doel.uuid).exists())

    def test_create_doel_with_valid_einddatums(self):
        url = reverse("plannen:doel-list")
        data = {
            **self.data,
            "startdatum": "2026-01-10",
            "einddatum": "2026-01-20",
            "beoogde_startdatum": "2026-01-10",
            "beoogde_einddatum": "2026-01-20",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_doel_einddatum_before_startdatum(self):
        url = reverse("plannen:doel-list")
        data = {
            **self.data,
            "startdatum": "2026-01-10",
            "einddatum": "2026-01-05",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "einddatum")
        self.assertEqual(error["reason"], self.DATUM_ERROR)
        self.assertFalse(Doel.objects.exists())

    def test_create_doel_einddatum_same_as_startdatum(self):
        url = reverse("plannen:doel-list")
        data = {
            **self.data,
            "startdatum": "2026-01-10",
            "einddatum": "2026-01-10",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "einddatum")
        self.assertEqual(error["reason"], self.DATUM_ERROR)

    def test_create_doel_beoogde_einddatum_before_beoogde_startdatum(self):
        url = reverse("plannen:doel-list")
        data = {
            **self.data,
            "beoogde_startdatum": "2026-01-10",
            "beoogde_einddatum": "2026-01-05",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "beoogdeEinddatum")
        self.assertEqual(error["reason"], self.BEOOGDE_EINDDATUM_ERROR)
        self.assertFalse(Doel.objects.exists())

    def test_partial_update_einddatum_before_existing_startdatum(self):
        doel = DoelFactory.create(startdatum=date(2026, 1, 10), einddatum=None)

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        response = self.client.patch(url, {"einddatum": "2026-01-05"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "einddatum")
        self.assertEqual(error["reason"], self.DATUM_ERROR)
        doel.refresh_from_db()
        self.assertIsNone(doel.einddatum)

    def test_partial_update_startdatum_after_existing_einddatum(self):
        doel = DoelFactory.create(
            startdatum=date(2026, 1, 10), einddatum=date(2026, 1, 20)
        )

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        response = self.client.patch(url, {"startdatum": "2026-01-25"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "einddatum")
        self.assertEqual(error["reason"], self.DATUM_ERROR)
        doel.refresh_from_db()
        self.assertEqual(doel.startdatum, date(2026, 1, 10))

    def test_partial_update_valid_einddatum(self):
        doel = DoelFactory.create(startdatum=date(2026, 1, 10), einddatum=None)

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        response = self.client.patch(url, {"einddatum": "2026-01-20"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doel.refresh_from_db()
        self.assertEqual(doel.einddatum, date(2026, 1, 20))

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:doel-list")

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_positie_uuid(self):
        doel_with_positie = DoelFactory(positie=self.positie)
        DoelFactory(
            positie=PositieFactory.create(),
        )

        url = reverse("plannen:doel-list")
        response = self.client.get(url, {"positie__uuid": str(self.positie.uuid)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["uuid"], str(doel_with_positie.uuid)
        )

    def test_filter_status(self):
        doel1 = DoelFactory(status=Status.ACTIEF)
        DoelFactory(status=Status.NIET_ACTIEF)

        url = reverse("plannen:doel-list")
        response = self.client.get(url, {"status": "actief"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(doel1.uuid))

    def test_filter_naam_icontains(self):
        doel1 = DoelFactory(naam="taalcursus")
        DoelFactory(naam="Rijden")

        url = reverse("plannen:doel-list")
        response = self.client.get(url, {"naam__icontains": "taal"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(doel1.uuid))

    def test_filter_resultaat(self):
        doel1 = DoelFactory(resultaat=Resultaat.BEHAALD)
        DoelFactory(resultaat=Resultaat.NIET_BEHAALD)

        url = reverse("plannen:doel-list")

        response = self.client.get(url, {"resultaat": "behaald"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(doel1.uuid))

    def test_startdatum_filter(self):
        doel1 = DoelFactory(
            startdatum=timezone.make_aware(datetime(2026, 1, 1)),
        )
        DoelFactory(
            startdatum=timezone.make_aware(datetime(2026, 2, 1)),
        )

        url = reverse("plannen:doel-list")

        with self.subTest("exact"):
            response = self.client.get(url, {"startdatum": "2026-01-01"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["uuid"], str(doel1.uuid))

        with self.subTest("lte"):
            response = self.client.get(url, {"startdatum__lte": "2026-01-31"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("gte"):
            response = self.client.get(url, {"startdatum__gte": "2026-02-01"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    def test_einddatum_filter(self):
        doel1 = DoelFactory(
            startdatum=timezone.make_aware(datetime(2026, 1, 1)),
            einddatum=timezone.make_aware(datetime(2026, 1, 15)),
        )
        DoelFactory(
            startdatum=timezone.make_aware(datetime(2026, 2, 1)),
            einddatum=timezone.make_aware(datetime(2026, 2, 15)),
        )

        url = reverse("plannen:doel-list")

        with self.subTest("exact"):
            response = self.client.get(url, {"einddatum": "2026-01-15"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["uuid"], str(doel1.uuid))

        with self.subTest("lte"):
            response = self.client.get(url, {"einddatum__lte": "2026-01-31"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("gte"):
            response = self.client.get(url, {"einddatum__gte": "2026-02-01"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    @patch.object(doelen_create_counter, "add", wraps=doelen_create_counter.add)
    def test_create_doel_increments_metric(self, mock_add: MagicMock):
        url = reverse("plannen:doel-list")

        response = self.client.post(url, self.data, format="json")
        self.assertEqual(response.status_code, 201)
        mock_add.assert_called_once_with(1)

    @patch.object(doelen_update_counter, "add", wraps=doelen_update_counter.add)
    def test_update_doel_increments_metric(self, mock_add: MagicMock):
        doel = DoelFactory.create(positie=self.positie)

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        data = {
            "positieUuid": str(doel.positie.uuid),
            "naam": "Test update Doel",
            "startdatum": str(date.today()),
            "beoogde_startdatum": date.today().isoformat(),
            "omschrijving": "Beschrijving update test",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        mock_add.assert_called_once_with(1)

    @patch.object(doelen_delete_counter, "add", wraps=doelen_delete_counter.add)
    def test_delete_doel_increments_metric(self, mock_add: MagicMock):
        doel = DoelFactory.create(positie=self.positie)
        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        response = self.client.delete(url)
        self.assertIn(response.status_code, (200, 204))
        mock_add.assert_called_once_with(1)
