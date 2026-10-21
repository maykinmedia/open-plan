from unittest.mock import MagicMock, patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from openplan.plannen.metrics import (
    doeltypen_create_counter,
    doeltypen_delete_counter,
    doeltypen_update_counter,
)
from openplan.plannen.models.factories.doeltype import DoelTypeFactory

from ...models.doeltype import DoelType
from .api_testcase import APITestCase


class DoelTypeAPITests(APITestCase):
    def setUp(self):
        super().setUp()

    def test_create_doeltype(self):
        url = reverse("plannen:doeltype-list")
        doeltype_data = DoelTypeFactory.build()
        data = {
            "naam": doeltype_data.naam,
            "omschrijving": doeltype_data.omschrijving,
            "status": doeltype_data.status,
            "gewenst_resultaat": doeltype_data.gewenst_resultaat,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doeltype = DoelType.objects.get(uuid=response.data["uuid"])
        self.assertEqual(doeltype.naam, data["naam"])
        self.assertEqual(doeltype.omschrijving, data["omschrijving"])
        self.assertEqual(doeltype.status, data["status"])
        self.assertEqual(doeltype.gewenst_resultaat, data["gewenst_resultaat"])

    def test_list_doeltypes(self):
        DoelTypeFactory.create_batch(2)

        url = reverse("plannen:doeltype-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 2)
        for dt in data:
            self.assertIn("uuid", dt)
            self.assertIn("naam", dt)
            self.assertIn("omschrijving", dt)
            self.assertIn("status", dt)
            self.assertIn("gewenstResultaat", dt)

    def test_retrieve_doeltype(self):
        doeltype = DoelTypeFactory.create()
        url = reverse("plannen:doeltype-detail", kwargs={"uuid": doeltype.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(doeltype.uuid))
        self.assertEqual(response.data["naam"], doeltype.naam)
        self.assertEqual(response.data["omschrijving"], doeltype.omschrijving)
        self.assertEqual(response.data["status"], doeltype.status)
        self.assertEqual(response.data["gewenst_resultaat"], doeltype.gewenst_resultaat)

    def test_update_doeltype(self):
        doeltype = DoelTypeFactory.create()
        new_doeltype = DoelTypeFactory.build()

        url = reverse("plannen:doeltype-detail", kwargs={"uuid": doeltype.uuid})
        data = {
            "naam": new_doeltype.naam,
            "omschrijving": new_doeltype.omschrijving,
            "status": new_doeltype.status,
            "gewenst_resultaat": new_doeltype.gewenst_resultaat,
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doeltype.refresh_from_db()
        self.assertEqual(doeltype.naam, new_doeltype.naam)
        self.assertEqual(doeltype.omschrijving, new_doeltype.omschrijving)
        self.assertEqual(doeltype.status, new_doeltype.status)
        self.assertEqual(doeltype.gewenst_resultaat, new_doeltype.gewenst_resultaat)

    def test_partial_update_doeltype(self):
        doeltype = DoelTypeFactory.create()
        new_naam = DoelTypeFactory.build().naam

        url = reverse("plannen:doeltype-detail", kwargs={"uuid": doeltype.uuid})
        data = {
            "naam": new_naam,
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doeltype.refresh_from_db()
        self.assertEqual(doeltype.naam, new_naam)

    def test_delete_doeltype(self):
        doeltype = DoelTypeFactory.create()
        url = reverse("plannen:doeltype-detail", kwargs={"uuid": doeltype.uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(DoelType.objects.filter(uuid=doeltype.uuid).exists())

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:doeltype-list")
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_doeltype_by_naam(self):
        doeltype_match = DoelTypeFactory.create(naam="hoofddoel")
        DoelTypeFactory.create(naam="werk")
        DoelTypeFactory.create(naam="inkomen")

        url = reverse("plannen:doeltype-list")
        response = self.client.get(url, {"naam": "hoofddoel"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["uuid"], str(doeltype_match.uuid))
        self.assertEqual(data["results"][0]["naam"], "hoofddoel")

    @patch.object(doeltypen_create_counter, "add", wraps=doeltypen_create_counter.add)
    def test_create_doeltype_increments_metric(self, mock_add: MagicMock):
        url = reverse("plannen:doeltype-list")
        data = {
            "naam": DoelTypeFactory.build().naam,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        mock_add.assert_called_once_with(1)

    @patch.object(doeltypen_update_counter, "add", wraps=doeltypen_update_counter.add)
    def test_update_doeltype_increments_metric(self, mock_add: MagicMock):
        doeltype = DoelTypeFactory.create()
        new_naam = DoelTypeFactory.build().naam

        url = reverse("plannen:doeltype-detail", kwargs={"uuid": doeltype.uuid})
        data = {
            "naam": new_naam,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        mock_add.assert_called_once_with(1)

    @patch.object(doeltypen_delete_counter, "add", wraps=doeltypen_delete_counter.add)
    def test_delete_doeltype_increments_metric(self, mock_add: MagicMock):
        doeltype = DoelTypeFactory.create()
        url = reverse("plannen:doeltype-detail", kwargs={"uuid": doeltype.uuid})
        response = self.client.delete(url)
        self.assertIn(response.status_code, (200, 204))
        mock_add.assert_called_once_with(1)
