from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from vng_api_common.tests import get_validation_errors

from openplan.plannen.enums.status import Typestatus
from openplan.plannen.models.factories.configuratie import ConfiguratieFactory
from openplan.plannen.models.factories.evaluatie import EvaluatieFactory
from openplan.plannen.models.factories.evaluatietype import EvaluatietypeFactory

from ...models.evaluatietype import Evaluatietype
from .api_testcase import APITestCase

ONBEKENDE_UUID = "00000000-0000-0000-0000-000000000000"


class EvaluatietypeAPITests(APITestCase):
    def setUp(self):
        super().setUp()
        self.configuratie = ConfiguratieFactory.create()

        self.data = {
            "configuratieUuids": [str(self.configuratie.uuid)],
            "naam": "Test Evaluatietype",
            "omschrijving": "Beschrijving test",
            "status": Typestatus.ACTIEF,
            "toelichtingInwoner": "Toelichting voor de inwoner",
            "toelichtingMedewerker": "Toelichting voor de medewerker",
        }

    def test_create_evaluatietype(self):
        url = reverse("plannen:evaluatietype-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        evaluatietype = Evaluatietype.objects.get(uuid=response.data["uuid"])
        self.assertEqual(evaluatietype.naam, "Test Evaluatietype")
        self.assertEqual(evaluatietype.omschrijving, "Beschrijving test")
        self.assertEqual(evaluatietype.status, Typestatus.ACTIEF)
        self.assertEqual(
            evaluatietype.toelichting_inwoner, "Toelichting voor de inwoner"
        )
        self.assertEqual(
            evaluatietype.toelichting_medewerker, "Toelichting voor de medewerker"
        )
        self.assertEqual(list(evaluatietype.configuraties.all()), [self.configuratie])

    def test_create_evaluatietype_returns_nested_configuraties(self):
        url = reverse("plannen:evaluatietype-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(len(data["configuraties"]), 1)
        self.assertEqual(data["configuraties"][0]["uuid"], str(self.configuratie.uuid))
        self.assertNotIn("configuratieUuids", data)

    def test_create_evaluatietype_with_multiple_configuraties(self):
        configuratie2 = ConfiguratieFactory.create()

        url = reverse("plannen:evaluatietype-list")
        data = {
            **self.data,
            "configuratieUuids": [str(self.configuratie.uuid), str(configuratie2.uuid)],
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        evaluatietype = Evaluatietype.objects.get(uuid=response.data["uuid"])
        self.assertEqual(evaluatietype.configuraties.count(), 2)

    def test_create_evaluatietype_without_configuraties(self):
        url = reverse("plannen:evaluatietype-list")
        data = {**self.data}
        del data["configuratieUuids"]
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "configuratieUuids")
        self.assertEqual(error["code"], "required")
        self.assertFalse(Evaluatietype.objects.exists())

    def test_create_evaluatietype_unknown_configuratie(self):
        url = reverse("plannen:evaluatietype-list")
        data = {**self.data, "configuratieUuids": [ONBEKENDE_UUID]}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(get_validation_errors(response, "configuratieUuids"))
        self.assertFalse(Evaluatietype.objects.exists())

    def test_list_evaluatietypes(self):
        EvaluatietypeFactory.create_batch(3)

        url = reverse("plannen:evaluatietype-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 3)

        for evaluatietype_data in data:
            self.assertIn("uuid", evaluatietype_data)

    def test_retrieve_evaluatietype(self):
        evaluatietype = EvaluatietypeFactory.create()

        url = reverse(
            "plannen:evaluatietype-detail", kwargs={"uuid": evaluatietype.uuid}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(evaluatietype.uuid))

    def test_retrieve_unknown_evaluatietype(self):
        url = reverse("plannen:evaluatietype-detail", kwargs={"uuid": ONBEKENDE_UUID})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_evaluatietype(self):
        evaluatietype = EvaluatietypeFactory.create()
        url = reverse(
            "plannen:evaluatietype-detail", kwargs={"uuid": evaluatietype.uuid}
        )
        data = {
            **self.data,
            "naam": "Test update Evaluatietype",
            "omschrijving": "Beschrijving update test",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        evaluatietype.refresh_from_db()
        self.assertEqual(evaluatietype.naam, "Test update Evaluatietype")
        self.assertEqual(evaluatietype.omschrijving, "Beschrijving update test")
        self.assertEqual(list(evaluatietype.configuraties.all()), [self.configuratie])

    def test_partial_update_evaluatietype(self):
        evaluatietype = EvaluatietypeFactory.create(naam="Origineel")

        url = reverse(
            "plannen:evaluatietype-detail", kwargs={"uuid": evaluatietype.uuid}
        )
        response = self.client.patch(url, {"naam": "Nieuwe naam"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        evaluatietype.refresh_from_db()
        self.assertEqual(evaluatietype.naam, "Nieuwe naam")

    def test_partial_update_status_niet_actief(self):
        evaluatietype = EvaluatietypeFactory.create(status=Typestatus.ACTIEF)

        url = reverse(
            "plannen:evaluatietype-detail", kwargs={"uuid": evaluatietype.uuid}
        )
        response = self.client.patch(
            url, {"status": Typestatus.NIET_ACTIEF}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        evaluatietype.refresh_from_db()
        self.assertEqual(evaluatietype.status, Typestatus.NIET_ACTIEF)

    def test_partial_update_replaces_configuraties(self):
        evaluatietype = EvaluatietypeFactory.create()
        evaluatietype.configuraties.set([self.configuratie])
        nieuwe_configuratie = ConfiguratieFactory.create()

        url = reverse(
            "plannen:evaluatietype-detail", kwargs={"uuid": evaluatietype.uuid}
        )
        response = self.client.patch(
            url,
            {"configuratieUuids": [str(nieuwe_configuratie.uuid)]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        evaluatietype.refresh_from_db()
        self.assertEqual(list(evaluatietype.configuraties.all()), [nieuwe_configuratie])

    def test_delete_evaluatietype(self):
        evaluatietype = EvaluatietypeFactory.create()

        url = reverse(
            "plannen:evaluatietype-detail", kwargs={"uuid": evaluatietype.uuid}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Evaluatietype.objects.filter(uuid=evaluatietype.uuid).exists())

    def test_delete_evaluatietype_in_use_returns_400(self):
        evaluatietype = EvaluatieFactory.create().evaluatietype

        url = reverse(
            "plannen:evaluatietype-detail", kwargs={"uuid": evaluatietype.uuid}
        )
        response = self.client.delete(url)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.json()
        )
        self.assertTrue(Evaluatietype.objects.filter(uuid=evaluatietype.uuid).exists())

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:evaluatietype-list")

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_naam(self):
        evaluatietype1 = EvaluatietypeFactory(naam="Tussentijdse evaluatie")
        EvaluatietypeFactory(naam="Eindevaluatie")

        url = reverse("plannen:evaluatietype-list")
        response = self.client.get(url, {"naam": "Tussentijdse evaluatie"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(evaluatietype1.uuid))

    def test_filter_naam_icontains(self):
        evaluatietype1 = EvaluatietypeFactory(naam="Tussentijdse evaluatie")
        EvaluatietypeFactory(naam="Eindevaluatie")

        url = reverse("plannen:evaluatietype-list")
        response = self.client.get(url, {"naam__icontains": "tussen"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(evaluatietype1.uuid))

    def test_filter_status(self):
        evaluatietype1 = EvaluatietypeFactory(status=Typestatus.ACTIEF)
        EvaluatietypeFactory(status=Typestatus.NIET_ACTIEF)

        url = reverse("plannen:evaluatietype-list")
        response = self.client.get(url, {"status": Typestatus.ACTIEF})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(evaluatietype1.uuid))

    def test_filter_omschrijving_icontains(self):
        evaluatietype1 = EvaluatietypeFactory(
            omschrijving="Gesprek met de inwoner over voortgang"
        )
        EvaluatietypeFactory(omschrijving="Iets anders")

        url = reverse("plannen:evaluatietype-list")
        response = self.client.get(url, {"omschrijving__icontains": "voortgang"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(evaluatietype1.uuid))

    def test_filter_configuratie_uuid(self):
        evaluatietype1 = EvaluatietypeFactory()
        evaluatietype1.configuraties.set([self.configuratie])
        evaluatietype2 = EvaluatietypeFactory()
        evaluatietype2.configuraties.set([ConfiguratieFactory.create()])

        url = reverse("plannen:evaluatietype-list")
        response = self.client.get(
            url, {"configuraties__uuid": str(self.configuratie.uuid)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(evaluatietype1.uuid))

    def test_filter_configuratie_uuids(self):
        configuratie2 = ConfiguratieFactory.create()
        evaluatietype1 = EvaluatietypeFactory()
        evaluatietype1.configuraties.set([self.configuratie])

        evaluatietype2 = EvaluatietypeFactory()
        evaluatietype2.configuraties.set([configuratie2])

        evaluatietype3 = EvaluatietypeFactory()
        evaluatietype3.configuraties.set([self.configuratie, configuratie2])

        EvaluatietypeFactory().configuraties.set([ConfiguratieFactory.create()])

        url = reverse("plannen:evaluatietype-list")
        response = self.client.get(
            url,
            {"configuraties__uuids": f"{self.configuratie.uuid},{configuratie2.uuid}"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(
            {result["uuid"] for result in response.data["results"]},
            {
                str(evaluatietype1.uuid),
                str(evaluatietype2.uuid),
                str(evaluatietype3.uuid),
            },
        )
