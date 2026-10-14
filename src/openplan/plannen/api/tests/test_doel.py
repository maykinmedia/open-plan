from datetime import date, datetime
from unittest.mock import MagicMock, patch

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from openplan.plannen.enums.status import PlanStatus, Resultaat
from openplan.plannen.metrics import (
    doelen_create_counter,
    doelen_delete_counter,
    doelen_update_counter,
)
from openplan.plannen.models.factories.doel import DoelFactory
from openplan.plannen.models.factories.persoon import PersoonFactory
from openplan.plannen.models.factories.plan import PlanFactory

from ...models.doel import Doel
from .api_testcase import APITestCase


# TODO UPDATE TEST AFTER V2 MODEL IS IMPLEMENTED
class DoelAPITests(APITestCase):
    def setUp(self):
        super().setUp()
        self.plan = PlanFactory.create()
        self.persoon = PersoonFactory.create()

        self.data = {
            "persoonUuid": str(self.persoon.uuid),
            "titel": "Test Doel",
            "startdatum": str(date.today()),
            "beschrijving": "Beschrijving test",
        }

    def test_create_doel(self):
        url = reverse("plannen:doel-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_doelens(self):
        DoelFactory.create_batch(3, persoon=self.persoon)

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
            "persoonUuid": str(doel.persoon.uuid),
            "titel": "Test update Doel",
            "startdatum": str(date.today()),
            "beschrijving": "Beschrijving update test",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doel.refresh_from_db()

    def test_partial_update_doel(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        data = {"titel": "New titel"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doel.refresh_from_db()

    def test_delete_doel(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doel.objects.filter(uuid=doel.uuid).exists())

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:doel-list")

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_persoon_uuid(self):
        doel_with_persoon = DoelFactory(persoon=self.persoon)
        DoelFactory(
            persoon=PersoonFactory.create(),
        )

        url = reverse("plannen:doel-list")
        response = self.client.get(url, {"persoon__uuid": str(self.persoon.uuid)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["uuid"], str(doel_with_persoon.uuid)
        )

    def test_filter_status(self):
        doel1 = DoelFactory(status=PlanStatus.ACTIEF)
        DoelFactory(status=PlanStatus.AFGEROND)

        url = reverse("plannen:doel-list")
        response = self.client.get(url, {"status": "actief"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(doel1.uuid))

    def test_filter_titel_icontains(self):
        doel1 = DoelFactory(titel="taalcursus")
        DoelFactory(titel="Rijden")

        url = reverse("plannen:doel-list")
        response = self.client.get(url, {"titel__icontains": "taal"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(doel1.uuid))

    def test_filter_resultaat(self):
        doel1 = DoelFactory(resultaat=Resultaat.BEHAALD)
        DoelFactory(resultaat=Resultaat.GEFAALD)

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
        doel = DoelFactory.create(persoon=self.persoon)
        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        data = {
            "persoonUuid": str(doel.persoon.uuid),
            "titel": "Test update Doel",
            "startdatum": str(date.today()),
            "beschrijving": "Beschrijving update test",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        mock_add.assert_called_once_with(1)

    @patch.object(doelen_delete_counter, "add", wraps=doelen_delete_counter.add)
    def test_delete_doel_increments_metric(self, mock_add: MagicMock):
        doel = DoelFactory.create(persoon=self.persoon)

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})

        response = self.client.delete(url)
        self.assertIn(response.status_code, (200, 204))
        mock_add.assert_called_once_with(1)
