from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from vng_api_common.tests import get_validation_errors

from openplan.plannen.enums.status import Typestatus
from openplan.plannen.models.factories.configuratie import ConfiguratieFactory
from openplan.plannen.models.factories.subdoel import SubdoelFactory
from openplan.plannen.models.factories.subdoeltype import SubdoelTypeFactory

from ...models.subdoeltype import SubdoelType
from .api_testcase import APITestCase

ONBEKENDE_UUID = "00000000-0000-0000-0000-000000000000"


class SubdoeltypeAPITests(APITestCase):
    def setUp(self):
        super().setUp()
        self.configuratie = ConfiguratieFactory.create()

        self.data = {
            "configuratieUuids": [str(self.configuratie.uuid)],
            "naam": "Test Subdoeltype",
            "omschrijving": "Beschrijving test",
            "status": Typestatus.ACTIEF,
            "gewenstResultaat": "Gewenst resultaat test",
            "toelichtingInwoner": "Toelichting voor de inwoner",
            "toelichtingMedewerker": "Toelichting voor de medewerker",
        }

    def test_create_subdoeltype(self):
        url = reverse("plannen:subdoeltype-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        subdoeltype = SubdoelType.objects.get(uuid=response.data["uuid"])
        self.assertEqual(subdoeltype.naam, "Test Subdoeltype")
        self.assertEqual(subdoeltype.status, Typestatus.ACTIEF)
        self.assertEqual(subdoeltype.gewenst_resultaat, "Gewenst resultaat test")
        self.assertEqual(subdoeltype.toelichting_inwoner, "Toelichting voor de inwoner")
        self.assertEqual(
            subdoeltype.toelichting_medewerker, "Toelichting voor de medewerker"
        )
        self.assertEqual(list(subdoeltype.configuraties.all()), [self.configuratie])

    def test_create_subdoeltype_returns_nested_configuraties(self):
        url = reverse("plannen:subdoeltype-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(len(data["configuraties"]), 1)
        self.assertEqual(data["configuraties"][0]["uuid"], str(self.configuratie.uuid))
        self.assertNotIn("configuratieUuids", data)

    def test_create_subdoeltype_with_multiple_configuraties(self):
        configuratie2 = ConfiguratieFactory.create()

        url = reverse("plannen:subdoeltype-list")
        data = {
            **self.data,
            "configuratieUuids": [str(self.configuratie.uuid), str(configuratie2.uuid)],
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        subdoeltype = SubdoelType.objects.get(uuid=response.data["uuid"])
        self.assertEqual(subdoeltype.configuraties.count(), 2)

    def test_create_subdoeltype_without_configuraties(self):
        url = reverse("plannen:subdoeltype-list")
        data = {**self.data}
        del data["configuratieUuids"]
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "configuratieUuids")
        self.assertEqual(error["code"], "required")
        self.assertFalse(SubdoelType.objects.exists())

    def test_create_subdoeltype_unknown_configuratie(self):
        url = reverse("plannen:subdoeltype-list")
        data = {**self.data, "configuratieUuids": [ONBEKENDE_UUID]}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(get_validation_errors(response, "configuratieUuids"))
        self.assertFalse(SubdoelType.objects.exists())

    def test_list_subdoeltypes(self):
        SubdoelTypeFactory.create_batch(3)

        url = reverse("plannen:subdoeltype-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 3)

        for subdoeltype_data in data:
            self.assertIn("uuid", subdoeltype_data)

    def test_retrieve_subdoeltype(self):
        subdoeltype = SubdoelTypeFactory.create()

        url = reverse("plannen:subdoeltype-detail", kwargs={"uuid": subdoeltype.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(subdoeltype.uuid))

    def test_retrieve_unknown_subdoeltype(self):
        url = reverse("plannen:subdoeltype-detail", kwargs={"uuid": ONBEKENDE_UUID})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_subdoeltype(self):
        subdoeltype = SubdoelTypeFactory.create()
        url = reverse("plannen:subdoeltype-detail", kwargs={"uuid": subdoeltype.uuid})
        data = {
            **self.data,
            "naam": "Test update Subdoeltype",
            "omschrijving": "Beschrijving update test",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        subdoeltype.refresh_from_db()
        self.assertEqual(subdoeltype.naam, "Test update Subdoeltype")
        self.assertEqual(subdoeltype.omschrijving, "Beschrijving update test")
        self.assertEqual(list(subdoeltype.configuraties.all()), [self.configuratie])

    def test_partial_update_subdoeltype(self):
        subdoeltype = SubdoelTypeFactory.create(naam="Origineel")

        url = reverse("plannen:subdoeltype-detail", kwargs={"uuid": subdoeltype.uuid})
        response = self.client.patch(url, {"naam": "Nieuwe naam"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        subdoeltype.refresh_from_db()
        self.assertEqual(subdoeltype.naam, "Nieuwe naam")

    def test_partial_update_status_niet_actief(self):
        subdoeltype = SubdoelTypeFactory.create(status=Typestatus.ACTIEF)

        url = reverse("plannen:subdoeltype-detail", kwargs={"uuid": subdoeltype.uuid})
        response = self.client.patch(
            url, {"status": Typestatus.NIET_ACTIEF}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        subdoeltype.refresh_from_db()
        self.assertEqual(subdoeltype.status, Typestatus.NIET_ACTIEF)

    def test_partial_update_replaces_configuraties(self):
        subdoeltype = SubdoelTypeFactory.create()
        subdoeltype.configuraties.set([self.configuratie])
        nieuwe_configuratie = ConfiguratieFactory.create()

        url = reverse("plannen:subdoeltype-detail", kwargs={"uuid": subdoeltype.uuid})
        response = self.client.patch(
            url,
            {"configuratieUuids": [str(nieuwe_configuratie.uuid)]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        subdoeltype.refresh_from_db()
        self.assertEqual(list(subdoeltype.configuraties.all()), [nieuwe_configuratie])

    def test_delete_subdoeltype(self):
        subdoeltype = SubdoelTypeFactory.create()

        url = reverse("plannen:subdoeltype-detail", kwargs={"uuid": subdoeltype.uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SubdoelType.objects.filter(uuid=subdoeltype.uuid).exists())

    def test_delete_subdoeltype_in_use_returns_400(self):
        subdoeltype = SubdoelFactory.create().subdoeltype

        url = reverse("plannen:subdoeltype-detail", kwargs={"uuid": subdoeltype.uuid})
        response = self.client.delete(url)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.json()
        )
        self.assertTrue(SubdoelType.objects.filter(uuid=subdoeltype.uuid).exists())

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:subdoeltype-list")

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_naam(self):
        subdoeltype1 = SubdoelTypeFactory(naam="Taalcursus")
        SubdoelTypeFactory(naam="Rijbewijs")

        url = reverse("plannen:subdoeltype-list")
        response = self.client.get(url, {"naam": "Taalcursus"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(subdoeltype1.uuid))

    def test_filter_naam_icontains(self):
        subdoeltype1 = SubdoelTypeFactory(naam="Taalcursus")
        SubdoelTypeFactory(naam="Rijbewijs")

        url = reverse("plannen:subdoeltype-list")
        response = self.client.get(url, {"naam__icontains": "taal"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(subdoeltype1.uuid))

    def test_filter_status(self):
        subdoeltype1 = SubdoelTypeFactory(status=Typestatus.ACTIEF)
        SubdoelTypeFactory(status=Typestatus.NIET_ACTIEF)

        url = reverse("plannen:subdoeltype-list")
        response = self.client.get(url, {"status": Typestatus.ACTIEF})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(subdoeltype1.uuid))

    def test_filter_omschrijving_icontains(self):
        subdoeltype1 = SubdoelTypeFactory(omschrijving="Leren fietsen in de stad")
        SubdoelTypeFactory(omschrijving="Iets anders")

        url = reverse("plannen:subdoeltype-list")
        response = self.client.get(url, {"omschrijving__icontains": "fietsen"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(subdoeltype1.uuid))

    def test_filter_configuratie_uuid(self):
        subdoeltype1 = SubdoelTypeFactory()
        subdoeltype1.configuraties.set([self.configuratie])
        subdoeltype2 = SubdoelTypeFactory()
        subdoeltype2.configuraties.set([ConfiguratieFactory.create()])

        url = reverse("plannen:subdoeltype-list")
        response = self.client.get(
            url, {"configuraties__uuid": str(self.configuratie.uuid)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(subdoeltype1.uuid))

    def test_filter_configuratie_uuids(self):
        configuratie2 = ConfiguratieFactory.create()
        subdoeltype1 = SubdoelTypeFactory()
        subdoeltype1.configuraties.set([self.configuratie])

        subdoeltype2 = SubdoelTypeFactory()
        subdoeltype2.configuraties.set([configuratie2])

        subdoeltype3 = SubdoelTypeFactory()
        subdoeltype3.configuraties.set([self.configuratie, configuratie2])

        SubdoelTypeFactory().configuraties.set([ConfiguratieFactory.create()])

        url = reverse("plannen:subdoeltype-list")
        response = self.client.get(
            url,
            {"configuraties__uuids": f"{self.configuratie.uuid},{configuratie2.uuid}"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(
            {result["uuid"] for result in response.data["results"]},
            {str(subdoeltype1.uuid), str(subdoeltype2.uuid), str(subdoeltype3.uuid)},
        )
