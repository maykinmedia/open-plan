from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from vng_api_common.tests import get_validation_errors

from openplan.plannen.models.factories.configuratie import ConfiguratieFactory
from openplan.plannen.models.factories.positietype import PositieTypeFactory

from ...models.positietype import PositieType
from .api_testcase import APITestCase

ONBEKENDE_UUID = "00000000-0000-4000-8000-000000000000"


class PositietypeAPITests(APITestCase):
    def setUp(self):
        super().setUp()
        self.configuratie = ConfiguratieFactory.create()

        self.data = {
            "configuratieUuids": [str(self.configuratie.uuid)],
            "naam": "Test Positietype",
            "omschrijving": "Beschrijving test",
            "toelichtingInwoner": "Toelichting voor de inwoner",
            "toelichtingMedewerker": "Toelichting voor de medewerker",
        }

    def test_create_positietype(self):
        url = reverse("plannen:positietype-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        positietype = PositieType.objects.get(uuid=response.data["uuid"])
        self.assertEqual(positietype.naam, "Test Positietype")
        self.assertEqual(positietype.toelichting_inwoner, "Toelichting voor de inwoner")
        self.assertEqual(list(positietype.configuraties.all()), [self.configuratie])

    def test_create_positietype_returns_nested_configuraties(self):
        url = reverse("plannen:positietype-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(len(data["configuraties"]), 1)
        self.assertEqual(data["configuraties"][0]["uuid"], str(self.configuratie.uuid))
        self.assertNotIn("configuratieUuids", data)

    def test_create_positietype_with_multiple_configuraties(self):
        configuratie2 = ConfiguratieFactory.create()

        url = reverse("plannen:positietype-list")
        data = {
            **self.data,
            "configuratieUuids": [str(self.configuratie.uuid), str(configuratie2.uuid)],
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        positietype = PositieType.objects.get(uuid=response.data["uuid"])
        self.assertEqual(positietype.configuraties.count(), 2)

    def test_create_positietype_without_configuraties(self):
        url = reverse("plannen:positietype-list")
        data = {**self.data}
        del data["configuratieUuids"]
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "configuratieUuids")
        self.assertEqual(error["code"], "required")
        self.assertFalse(PositieType.objects.exists())

    def test_create_positietype_unknown_configuratie(self):
        url = reverse("plannen:positietype-list")
        data = {**self.data, "configuratieUuids": [ONBEKENDE_UUID]}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(get_validation_errors(response, "configuratieUuids"))
        self.assertFalse(PositieType.objects.exists())

    def test_create_positietype_with_doelpositie(self):
        doelpositie = PositieTypeFactory.create()

        url = reverse("plannen:positietype-list")
        data = {**self.data, "doelpositie": str(doelpositie.uuid)}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        self.assertEqual(response.data["doelpositie"], str(doelpositie.uuid))
        positietype = PositieType.objects.get(uuid=response.data["uuid"])
        self.assertEqual(positietype.doelpositie, doelpositie)

    def test_create_positietype_with_doelpositie_null(self):
        url = reverse("plannen:positietype-list")
        data = {**self.data, "doelpositie": None}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        positietype = PositieType.objects.get(uuid=response.data["uuid"])
        self.assertIsNone(positietype.doelpositie)

    def test_create_positietype_unknown_doelpositie(self):
        url = reverse("plannen:positietype-list")
        data = {**self.data, "doelpositie": ONBEKENDE_UUID}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        invalid_params = response.json()["invalidParams"]
        self.assertEqual(invalid_params[0]["name"], "doelpositie")
        self.assertFalse(PositieType.objects.exists())

    def test_list_positietypes(self):
        PositieTypeFactory.create_batch(3)

        url = reverse("plannen:positietype-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 3)

        for positietype_data in data:
            self.assertIn("uuid", positietype_data)

    def test_retrieve_positietype(self):
        positietype = PositieTypeFactory.create()

        url = reverse("plannen:positietype-detail", kwargs={"uuid": positietype.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(positietype.uuid))

    def test_retrieve_unknown_positietype(self):
        url = reverse("plannen:positietype-detail", kwargs={"uuid": ONBEKENDE_UUID})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_positietype(self):
        positietype = PositieTypeFactory.create()
        url = reverse("plannen:positietype-detail", kwargs={"uuid": positietype.uuid})
        data = {
            **self.data,
            "naam": "Test update Positietype",
            "omschrijving": "Beschrijving update test",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        positietype.refresh_from_db()
        self.assertEqual(positietype.naam, "Test update Positietype")
        self.assertEqual(positietype.omschrijving, "Beschrijving update test")
        self.assertEqual(list(positietype.configuraties.all()), [self.configuratie])

    def test_partial_update_positietype(self):
        positietype = PositieTypeFactory.create(naam="Origineel")

        url = reverse("plannen:positietype-detail", kwargs={"uuid": positietype.uuid})
        response = self.client.patch(url, {"naam": "Nieuwe naam"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        positietype.refresh_from_db()
        self.assertEqual(positietype.naam, "Nieuwe naam")

    def test_partial_update_replaces_configuraties(self):
        positietype = PositieTypeFactory.create()
        positietype.configuraties.set([self.configuratie])
        nieuwe_configuratie = ConfiguratieFactory.create()

        url = reverse("plannen:positietype-detail", kwargs={"uuid": positietype.uuid})
        response = self.client.patch(
            url,
            {"configuratieUuids": [str(nieuwe_configuratie.uuid)]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        positietype.refresh_from_db()
        self.assertEqual(list(positietype.configuraties.all()), [nieuwe_configuratie])

    def test_partial_update_clear_doelpositie(self):
        doelpositie = PositieTypeFactory.create()
        positietype = PositieTypeFactory.create(doelpositie=doelpositie)

        url = reverse("plannen:positietype-detail", kwargs={"uuid": positietype.uuid})
        response = self.client.patch(url, {"doelpositie": None}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        positietype.refresh_from_db()
        self.assertIsNone(positietype.doelpositie)

    def test_delete_positietype(self):
        positietype = PositieTypeFactory.create()

        url = reverse("plannen:positietype-detail", kwargs={"uuid": positietype.uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PositieType.objects.filter(uuid=positietype.uuid).exists())

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:positietype-list")

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_naam_icontains(self):
        positietype1 = PositieTypeFactory(naam="Werkzoekend")
        PositieTypeFactory(naam="Studerend")

        url = reverse("plannen:positietype-list")
        response = self.client.get(url, {"naam__icontains": "werk"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(positietype1.uuid))

    def test_update_doelpositie_closing_a_loop(self):
        b = PositieTypeFactory.create()
        a = PositieTypeFactory.create(doelpositie=b)

        url = reverse("plannen:positietype-detail", kwargs={"uuid": b.uuid})
        response = self.client.patch(url, {"doelpositie": str(a.uuid)}, format="json")

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.json()
        )
        error = get_validation_errors(response, "doelpositie")
        self.assertEqual(error["code"], "cycle")
        b.refresh_from_db()
        self.assertIsNone(b.doelpositie)

    def test_update_doelpositie_extending_a_chain(self):
        b = PositieTypeFactory.create()
        PositieTypeFactory.create(doelpositie=b)
        c = PositieTypeFactory.create()

        url = reverse("plannen:positietype-detail", kwargs={"uuid": b.uuid})
        response = self.client.patch(url, {"doelpositie": str(c.uuid)}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        b.refresh_from_db()
        self.assertEqual(b.doelpositie, c)

    def test_create_doelpositie_pointing_into_a_chain(self):
        b = PositieTypeFactory.create()
        a = PositieTypeFactory.create(doelpositie=b)

        url = reverse("plannen:positietype-list")
        response = self.client.post(
            url, {**self.data, "doelpositie": str(a.uuid)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
