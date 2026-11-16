from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from openplan.plannen.models.factories.positie import PositieFactory
from openplan.plannen.models.factories.positietype import PositieTypeFactory
from openplan.plannen.models.factories.subject import SubjectFactory

from ...models.positie import Positie
from .api_testcase import APITestCase


class PositieAPITests(APITestCase):
    def setUp(self):
        super().setUp()
        self.subject = SubjectFactory.create()
        self.positietype = PositieTypeFactory.create()

        self.data = {
            "subjectUuid": str(self.subject.uuid),
            "positietypeUuid": str(self.positietype.uuid),
            "naam": "Test Positie",
            "omschrijving": "Beschrijving test",
        }

    def test_create_positie(self):
        url = reverse("plannen:positie-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        positie = Positie.objects.get(uuid=response.data["uuid"])
        self.assertEqual(positie.naam, "Test Positie")
        self.assertEqual(positie.subject, self.subject)
        self.assertEqual(positie.positietype, self.positietype)

    def test_create_positie_returns_nested_relations(self):
        url = reverse("plannen:positie-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["subject"]["uuid"], str(self.subject.uuid))
        self.assertEqual(data["positietype"]["uuid"], str(self.positietype.uuid))
        self.assertNotIn("subjectUuid", data)
        self.assertNotIn("positietypeUuid", data)

    def test_create_positie_without_subject(self):
        url = reverse("plannen:positie-list")
        data = {**self.data}
        del data["subjectUuid"]
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        invalid_params = response.json()["invalidParams"]
        self.assertEqual(invalid_params[0]["name"], "subjectUuid")
        self.assertFalse(Positie.objects.exists())

    def test_create_positie_without_positietype(self):
        url = reverse("plannen:positie-list")
        data = {**self.data}
        del data["positietypeUuid"]
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        invalid_params = response.json()["invalidParams"]
        self.assertEqual(invalid_params[0]["name"], "positietypeUuid")
        self.assertFalse(Positie.objects.exists())

    def test_create_positie_unknown_subject(self):
        url = reverse("plannen:positie-list")
        data = {
            **self.data,
            "subjectUuid": "00000000-0000-4000-8000-000000000000",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        invalid_params = response.json()["invalidParams"]
        self.assertEqual(invalid_params[0]["name"], "subjectUuid")
        self.assertFalse(Positie.objects.exists())

    def test_list_posities(self):
        PositieFactory.create_batch(3, subject=self.subject)

        url = reverse("plannen:positie-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 3)

        for positie_data in data:
            self.assertIn("uuid", positie_data)

    def test_retrieve_positie(self):
        positie = PositieFactory.create()

        url = reverse("plannen:positie-detail", kwargs={"uuid": positie.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(positie.uuid))

    def test_retrieve_unknown_positie(self):
        url = reverse(
            "plannen:positie-detail",
            kwargs={"uuid": "00000000-0000-4000-8000-000000000000"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_positie(self):
        positie = PositieFactory.create()
        url = reverse("plannen:positie-detail", kwargs={"uuid": positie.uuid})
        data = {
            "subjectUuid": str(positie.subject.uuid),
            "positietypeUuid": str(positie.positietype.uuid),
            "naam": "Test update Positie",
            "omschrijving": "Beschrijving update test",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        positie.refresh_from_db()
        self.assertEqual(positie.naam, "Test update Positie")
        self.assertEqual(positie.omschrijving, "Beschrijving update test")

    def test_partial_update_positie(self):
        positie = PositieFactory.create(naam="Origineel")

        url = reverse("plannen:positie-detail", kwargs={"uuid": positie.uuid})
        response = self.client.patch(url, {"naam": "Nieuwe naam"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        positie.refresh_from_db()
        self.assertEqual(positie.naam, "Nieuwe naam")

    def test_partial_update_positietype(self):
        positie = PositieFactory.create()
        nieuw_positietype = PositieTypeFactory.create()

        url = reverse("plannen:positie-detail", kwargs={"uuid": positie.uuid})
        response = self.client.patch(
            url, {"positietypeUuid": str(nieuw_positietype.uuid)}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        positie.refresh_from_db()
        self.assertEqual(positie.positietype, nieuw_positietype)

    def test_delete_positie(self):
        positie = PositieFactory.create()

        url = reverse("plannen:positie-detail", kwargs={"uuid": positie.uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Positie.objects.filter(uuid=positie.uuid).exists())

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:positie-list")

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_subject_uuid(self):
        positie_with_subject = PositieFactory(subject=self.subject)
        PositieFactory(subject=SubjectFactory.create())

        url = reverse("plannen:positie-list")
        response = self.client.get(url, {"subject__uuid": str(self.subject.uuid)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["uuid"], str(positie_with_subject.uuid)
        )

    def test_filter_naam_icontains(self):
        positie1 = PositieFactory(naam="Werkzoekende")
        PositieFactory(naam="Student")

        url = reverse("plannen:positie-list")
        response = self.client.get(url, {"naam__icontains": "werk"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(positie1.uuid))
