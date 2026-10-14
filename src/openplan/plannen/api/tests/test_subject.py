from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from openplan.plannen.models.factories.plan import PlanFactory

# from openplan.plannen.metrics import (
#     personen_create_counter,
#     personen_delete_counter,
#     personen_update_counter,
# )
from openplan.plannen.models.factories.subject import SubjectFactory

from ...models.subject import Subject
from .api_testcase import APITestCase


class SubjectAPITests(APITestCase):
    def test_create_subject(self):
        plan = PlanFactory.create()
        url = reverse("plannen:subject-list")
        data = {
            "plan": str(plan.uuid),
            "profiel": "urn:example:persoon:12345",
            "klant": "urn:example:klant:67890",
            "bsn": "963773215",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        subject = Subject.objects.get(uuid=response.data["uuid"])
        self.assertEqual(subject.profiel, data["profiel"])
        self.assertEqual(subject.klant, data["klant"])
        self.assertEqual(subject.bsn, data["bsn"])

    def test_list_subjecten(self):
        SubjectFactory.create_batch(3)

        url = reverse("plannen:subject-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 3)
        for p in data:
            self.assertIn("uuid", p)
            self.assertIn("profiel", p)
            self.assertIn("klant", p)
            self.assertIn("bsn", p)

    def test_retrieve_subject(self):
        subject = SubjectFactory.create()
        url = reverse("plannen:subject-detail", kwargs={"uuid": subject.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(subject.uuid))
        self.assertEqual(response.data["profiel"], subject.profiel)
        self.assertEqual(response.data["klant"], subject.klant)
        self.assertEqual(response.data["bsn"], subject.bsn)

    def test_update_subject(self):
        subject = SubjectFactory.create()
        plan = PlanFactory.create()
        new_data = {
            "plan": str(plan.uuid),
            "profiel": "urn:example:persoon:12345",
            "klant": "urn:example:klant:67890",
            "bsn": "111222333",
        }
        url = reverse("plannen:subject-detail", kwargs={"uuid": subject.uuid})
        response = self.client.put(url, new_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subject.refresh_from_db()
        self.assertEqual(subject.profiel, new_data["profiel"])
        self.assertEqual(subject.klant, new_data["klant"])
        self.assertEqual(subject.bsn, new_data["bsn"])

    def test_partial_update_subject(self):
        subject = SubjectFactory.create()
        new_data = {"bsn": "111222333"}
        url = reverse("plannen:subject-detail", kwargs={"uuid": subject.uuid})
        response = self.client.patch(url, new_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subject.refresh_from_db()
        self.assertEqual(subject.bsn, new_data["bsn"])

    def test_delete_subject(self):
        subject = SubjectFactory.create()
        url = reverse("plannen:subject-detail", kwargs={"uuid": subject.uuid})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subject.objects.filter(uuid=subject.uuid).exists())

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:subject-list")
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # @patch.object(personen_create_counter, "add", wraps=personen_create_counter.add)
    # def test_create_persoon_increments_metric(self, mock_add: MagicMock):
    #     url = reverse("plannen:persoon-list")
    #     data = {
    #         "persoonsprofiel": "urn:example:persoon:12345",
    #         "klant": "urn:example:klant:67890",
    #         "bsn": "963773215",
    #     }
    #     response = self.client.post(url, data, format="json")
    #     self.assertEqual(response.status_code, 201)
    #     mock_add.assert_called_once_with(1)

    # @patch.object(personen_update_counter, "add", wraps=personen_update_counter.add)
    # def test_update_persoon_increments_metric(self, mock_add: MagicMock):
    #     persoon = PersoonFactory.create()
    #     new_data = {"bsn": "111222333"}
    #     url = reverse("plannen:persoon-detail", kwargs={"uuid": persoon.uuid})
    #     response = self.client.patch(url, new_data, format="json")
    #     self.assertEqual(response.status_code, 200)
    #     mock_add.assert_called_once_with(1)

    # @patch.object(personen_delete_counter, "add", wraps=personen_delete_counter.add)
    # def test_delete_persoon_increments_metric(self, mock_add: MagicMock):
    #     persoon = PersoonFactory.create()
    #     url = reverse("plannen:persoon-detail", kwargs={"uuid": persoon.uuid})
    #     response = self.client.delete(url)
    #     self.assertIn(response.status_code, (200, 204))
    #     mock_add.assert_called_once_with(1)
