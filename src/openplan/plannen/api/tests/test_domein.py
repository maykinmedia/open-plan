from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from openplan.plannen.models.factories.domein import DomeinFactory

from ...enums.status import Status
from ...models.domein import Domein
from .api_testcase import APITestCase


class DomeinAPITests(APITestCase):
    def setUp(self):
        super().setUp()

        self.data = {
            "naam": "Test Domein",
            "omschrijving": "Beschrijving test domein",
            "status": Status.ACTIEF,
        }

    def test_create_domein(self):
        url = reverse("plannen:domein-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        domein = Domein.objects.get(uuid=response.data["uuid"])
        self.assertEqual(domein.naam, "Test Domein")
        self.assertEqual(domein.omschrijving, "Beschrijving test domein")
        self.assertEqual(domein.status, Status.ACTIEF)

    def test_list_domeinen(self):
        DomeinFactory.create_batch(3)

        url = reverse("plannen:domein-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 3)

        for domein_data in data:
            self.assertIn("uuid", domein_data)

    def test_retrieve_domein(self):
        domein = DomeinFactory.create()

        url = reverse("plannen:domein-detail", kwargs={"uuid": domein.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(domein.uuid))

    def test_update_domein(self):
        domein = DomeinFactory.create()

        url = reverse("plannen:domein-detail", kwargs={"uuid": domein.uuid})
        data = {
            "naam": "Test update Domein",
            "omschrijving": "Beschrijving update test",
            "status": Status.NIET_ACTIEF,
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        domein.refresh_from_db()
        self.assertEqual(domein.naam, "Test update Domein")
        self.assertEqual(domein.omschrijving, "Beschrijving update test")
        self.assertEqual(domein.status, Status.NIET_ACTIEF)

    def test_partial_update_domein(self):
        domein = DomeinFactory.create()

        url = reverse("plannen:domein-detail", kwargs={"uuid": domein.uuid})
        data = {"naam": "New domein naam"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        domein.refresh_from_db()
        self.assertEqual(domein.naam, "New domein naam")

    def test_delete_domein(self):
        domein = DomeinFactory.create()

        url = reverse("plannen:domein-detail", kwargs={"uuid": domein.uuid})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Domein.objects.filter(uuid=domein.uuid).exists())

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:domein-list")

        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_naam_exact(self):
        domein1 = DomeinFactory.create(naam="Onderwijs")
        DomeinFactory.create(naam="Zorg")

        url = reverse("plannen:domein-list")
        response = self.client.get(url, {"naam": "Onderwijs"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(domein1.uuid))

    def test_filter_naam_icontains(self):
        domein1 = DomeinFactory.create(naam="Onderwijs en ontwikkeling")
        DomeinFactory.create(naam="Zorg")

        url = reverse("plannen:domein-list")
        response = self.client.get(url, {"naam__icontains": "onderwijs"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(domein1.uuid))

    def test_filter_omschrijving_icontains(self):
        domein1 = DomeinFactory.create(omschrijving="Dit domein gaat over onderwijs")
        DomeinFactory.create(omschrijving="Dit domein gaat over zorg")

        url = reverse("plannen:domein-list")
        response = self.client.get(url, {"omschrijving__icontains": "onderwijs"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(domein1.uuid))

    def test_filter_status(self):
        domein1 = DomeinFactory.create(status=Status.ACTIEF)
        DomeinFactory.create(status=Status.NIET_ACTIEF)

        url = reverse("plannen:domein-list")
        response = self.client.get(url, {"status": "actief"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(domein1.uuid))
