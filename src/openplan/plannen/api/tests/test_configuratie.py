from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from openplan.plannen.models.factories.configuratie import ConfiguratieFactory
from openplan.plannen.models.factories.domein import DomeinFactory

from ...enums.status import Status
from ...models.configuratie import Configuratie
from .api_testcase import APITestCase


class ConfiguratieAPITests(APITestCase):
    def setUp(self):
        super().setUp()

        self.domein = DomeinFactory.create()

        self.data = {
            "domein_uuid": str(self.domein.uuid),
            "naam": "Test Configuratie",
            "omschrijving": "Beschrijving test configuratie",
            "status": Status.ACTIEF,
        }

    def test_create_configuratie(self):
        url = reverse("plannen:configuratie-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        configuratie = Configuratie.objects.get(uuid=response.data["uuid"])
        self.assertEqual(configuratie.naam, "Test Configuratie")
        self.assertEqual(configuratie.omschrijving, "Beschrijving test configuratie")
        self.assertEqual(configuratie.domein, self.domein)

    def test_list_configuraties(self):
        ConfiguratieFactory.create_batch(3, domein=self.domein)

        url = reverse("plannen:configuratie-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 3)

        for configuratie_data in data:
            self.assertIn("uuid", configuratie_data)
            self.assertIn("domein", configuratie_data)

    def test_retrieve_configuratie(self):
        configuratie = ConfiguratieFactory.create(domein=self.domein)

        url = reverse(
            "plannen:configuratie-detail",
            kwargs={"uuid": configuratie.uuid},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(configuratie.uuid))
        self.assertEqual(
            response.data["domein"]["uuid"],
            str(self.domein.uuid),
        )

    def test_update_configuratie(self):
        configuratie = ConfiguratieFactory.create(domein=self.domein)
        nieuw_domein = DomeinFactory.create()

        url = reverse(
            "plannen:configuratie-detail",
            kwargs={"uuid": configuratie.uuid},
        )
        data = {
            "domein_uuid": str(nieuw_domein.uuid),
            "naam": "Test update Configuratie",
            "omschrijving": "Beschrijving update test",
            "status": Status.NIET_ACTIEF,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        configuratie.refresh_from_db()
        self.assertEqual(configuratie.naam, "Test update Configuratie")
        self.assertEqual(configuratie.omschrijving, "Beschrijving update test")
        self.assertEqual(configuratie.status, Status.NIET_ACTIEF)
        self.assertEqual(configuratie.domein, nieuw_domein)

    def test_partial_update_configuratie(self):
        configuratie = ConfiguratieFactory.create(domein=self.domein)

        url = reverse(
            "plannen:configuratie-detail",
            kwargs={"uuid": configuratie.uuid},
        )
        data = {"naam": "New configuratie naam"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        configuratie.refresh_from_db()
        self.assertEqual(configuratie.naam, "New configuratie naam")

    def test_partial_update_domein(self):
        configuratie = ConfiguratieFactory.create(domein=self.domein)
        nieuw_domein = DomeinFactory.create()

        url = reverse(
            "plannen:configuratie-detail",
            kwargs={"uuid": configuratie.uuid},
        )
        data = {"domein_uuid": str(nieuw_domein.uuid)}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        configuratie.refresh_from_db()
        self.assertEqual(configuratie.domein, nieuw_domein)

    def test_delete_configuratie(self):
        configuratie = ConfiguratieFactory.create(domein=self.domein)

        url = reverse(
            "plannen:configuratie-detail",
            kwargs={"uuid": configuratie.uuid},
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Configuratie.objects.filter(uuid=configuratie.uuid).exists())

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:configuratie-list")

        response = client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_domein_uuid(self):
        configuratie1 = ConfiguratieFactory.create(domein=self.domein)
        ConfiguratieFactory.create(domein=DomeinFactory.create())

        url = reverse("plannen:configuratie-list")
        response = self.client.get(
            url,
            {"domein__uuid": str(self.domein.uuid)},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["uuid"],
            str(configuratie1.uuid),
        )

    def test_filter_naam_exact(self):
        configuratie1 = ConfiguratieFactory.create(
            naam="Onderwijs",
            domein=self.domein,
        )
        ConfiguratieFactory.create(
            naam="Zorg",
            domein=self.domein,
        )

        url = reverse("plannen:configuratie-list")
        response = self.client.get(url, {"naam": "Onderwijs"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["uuid"],
            str(configuratie1.uuid),
        )

    def test_filter_naam_icontains(self):
        configuratie1 = ConfiguratieFactory.create(
            naam="Onderwijs en ontwikkeling",
            domein=self.domein,
        )
        ConfiguratieFactory.create(
            naam="Zorg",
            domein=self.domein,
        )

        url = reverse("plannen:configuratie-list")
        response = self.client.get(url, {"naam__icontains": "onderwijs"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["uuid"],
            str(configuratie1.uuid),
        )

    def test_filter_omschrijving_icontains(self):
        configuratie1 = ConfiguratieFactory.create(
            omschrijving="Dit gaat over werk",
            domein=self.domein,
        )
        ConfiguratieFactory.create(
            omschrijving="Dit gaat over inkomen",
            domein=self.domein,
        )

        url = reverse("plannen:configuratie-list")
        response = self.client.get(
            url,
            {"omschrijving__icontains": "werk"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["uuid"],
            str(configuratie1.uuid),
        )

    def test_filter_status(self):
        configuratie1 = ConfiguratieFactory.create(
            status=Status.ACTIEF,
            domein=self.domein,
        )
        ConfiguratieFactory.create(
            status=Status.NIET_ACTIEF,
            domein=self.domein,
        )

        url = reverse("plannen:configuratie-list")
        response = self.client.get(url, {"status": "actief"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["uuid"],
            str(configuratie1.uuid),
        )
