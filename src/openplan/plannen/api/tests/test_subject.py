from unittest.mock import MagicMock, patch

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.test import APIClient
from vng_api_common.tests import get_validation_errors

from openplan.plannen.metrics import (
    subjecten_create_counter,
    subjecten_delete_counter,
    subjecten_update_counter,
)
from openplan.plannen.models.factories.plan import PlanFactory
from openplan.plannen.models.factories.subject import SubjectFactory

from ...enums.status import SubjectType
from ...models.subject import Subject
from .api_testcase import APITestCase


class SubjectAPITests(APITestCase):
    PERSOON_ERROR = _("Bij subjecttype 'persoon' is een klant of BSN verplicht.")
    FYSIEK_OBJECT_ERROR = _(
        "Bij subjecttype 'fysiek_object' is een ruimtelijk object verplicht."
    )
    PERSOON_RUIMTELIJK_OBJECT_ERROR = _(
        "Bij subjecttype 'persoon' mag geen ruimtelijk object worden opgegeven."
    )
    FYSIEK_OBJECT_KLANT_BSN_ERROR = _(
        "Bij subjecttype 'fysiek_object' mag geen klant of BSN worden opgegeven."
    )

    def setUp(self):
        super().setUp()
        self.plan = PlanFactory.create()
        self.data = {"planUuid": str(self.plan.uuid)}

    def test_create_subject(self):
        plan = PlanFactory.create()
        url = reverse("plannen:subject-list")
        data = {
            "planUuid": str(plan.uuid),
            "subjecttype": SubjectType.PERSOON,
            "profiel": "urn:example:persoon:uuid:3f1e9c2a-7b4d-4e8a-9c1f-2a6b5d8e0f17",
            "klant": "urn:example:klant:uuid:a8d2f4b6-1c3e-4f5a-8b7c-9d0e1f2a3b4c",
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
        new_data = {
            "subjecttype": SubjectType.PERSOON,
            "profiel": "urn:example:persoon:uuid:4f1e9c2a-7b4d-4e8a-9c1f-2a6b5d8e0f17",
            "klant": "urn:example:klant:uuid:b8d2f4b6-1c3e-4f5a-8b7c-9d0e1f2a3b4c",
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

    def test_patch_plan_returns_400_and_does_not_write(self):
        subject = SubjectFactory.create()
        original_plan = subject.plan

        url = reverse("plannen:subject-detail", kwargs={"uuid": subject.uuid})
        data = {
            "planUuid": str(PlanFactory.create().uuid),
        }

        response = self.client.patch(url, data, format="json")

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.json()
        )
        invalid_params = response.json()["invalidParams"]
        self.assertEqual(len(invalid_params), 1)

        subject.refresh_from_db()
        self.assertEqual(subject.plan, original_plan)

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

    def test_create_persoon_with_klant(self):
        url = reverse("plannen:subject-list")
        data = {
            **self.data,
            "subjecttype": SubjectType.PERSOON,
            "klant": "urn:example:klant:67890",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_persoon_with_bsn(self):
        url = reverse("plannen:subject-list")
        data = {
            **self.data,
            "subjecttype": SubjectType.PERSOON,
            "bsn": "963773215",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_persoon_without_klant_and_bsn(self):
        url = reverse("plannen:subject-list")
        data = {
            **self.data,
            "subjecttype": SubjectType.PERSOON,
            "profiel": "urn:example:persoon:12345",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "klant")
        self.assertEqual(error["reason"], self.PERSOON_ERROR)
        error = get_validation_errors(response, "bsn")
        self.assertEqual(error["reason"], self.PERSOON_ERROR)
        self.assertFalse(Subject.objects.exists())

    def test_create_persoon_with_ruimtelijk_object(self):
        url = reverse("plannen:subject-list")
        data = {
            **self.data,
            "subjecttype": SubjectType.PERSOON,
            "bsn": "963773215",
            "ruimtelijk_object": "urn:example:object:123",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "ruimtelijkObject")
        self.assertEqual(error["reason"], self.PERSOON_RUIMTELIJK_OBJECT_ERROR)
        self.assertFalse(Subject.objects.exists())

    def test_create_fysiek_object_with_ruimtelijk_object(self):
        url = reverse("plannen:subject-list")
        data = {
            **self.data,
            "subjecttype": SubjectType.FYSIEK_OBJECT,
            "ruimtelijk_object": "urn:example:object:123",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_fysiek_object_without_ruimtelijk_object(self):
        url = reverse("plannen:subject-list")
        data = {
            **self.data,
            "subjecttype": SubjectType.FYSIEK_OBJECT,
            "profiel": "urn:example:profiel:123",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "ruimtelijkObject")
        self.assertEqual(error["reason"], self.FYSIEK_OBJECT_ERROR)
        self.assertFalse(Subject.objects.exists())

    def test_create_fysiek_object_with_klant(self):
        url = reverse("plannen:subject-list")
        data = {
            **self.data,
            "subjecttype": SubjectType.FYSIEK_OBJECT,
            "ruimtelijk_object": "urn:example:object:123",
            "klant": "urn:example:klant:67890",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "klant")
        self.assertEqual(error["reason"], self.FYSIEK_OBJECT_KLANT_BSN_ERROR)
        self.assertFalse(Subject.objects.exists())

    def test_create_fysiek_object_with_bsn(self):
        url = reverse("plannen:subject-list")
        data = {
            **self.data,
            "subjecttype": SubjectType.FYSIEK_OBJECT,
            "ruimtelijk_object": "urn:example:object:123",
            "bsn": "963773215",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "bsn")
        self.assertEqual(error["reason"], self.FYSIEK_OBJECT_KLANT_BSN_ERROR)
        self.assertFalse(Subject.objects.exists())

    def test_partial_update_persoon_remove_klant_without_bsn(self):
        subject = SubjectFactory.create(
            subjecttype=SubjectType.PERSOON,
            klant="urn:example:klant:67890",
            bsn="",
        )

        url = reverse("plannen:subject-detail", kwargs={"uuid": subject.uuid})
        response = self.client.patch(url, {"klant": ""}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "klant")
        self.assertEqual(error["reason"], self.PERSOON_ERROR)
        subject.refresh_from_db()
        self.assertEqual(subject.klant, "urn:example:klant:67890")

    def test_partial_update_persoon_remove_klant_with_existing_bsn(self):
        subject = SubjectFactory.create(
            subjecttype=SubjectType.PERSOON,
            klant="urn:example:klant:67890",
            bsn="963773215",
        )

        url = reverse("plannen:subject-detail", kwargs={"uuid": subject.uuid})
        response = self.client.patch(url, {"klant": ""}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subject.refresh_from_db()
        self.assertEqual(subject.klant, "")

    def test_partial_update_subjecttype_to_fysiek_object_without_ruimtelijk_object(
        self,
    ):
        subject = SubjectFactory.create(
            subjecttype=SubjectType.PERSOON,
            bsn="963773215",
            ruimtelijk_object="",
        )

        url = reverse("plannen:subject-detail", kwargs={"uuid": subject.uuid})
        response = self.client.patch(
            url, {"subjecttype": SubjectType.FYSIEK_OBJECT}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "ruimtelijkObject")
        self.assertEqual(error["reason"], self.FYSIEK_OBJECT_ERROR)
        subject.refresh_from_db()
        self.assertEqual(subject.subjecttype, SubjectType.PERSOON)

    def test_partial_update_persoon_add_ruimtelijk_object(self):
        subject = SubjectFactory.create(
            subjecttype=SubjectType.PERSOON,
            bsn="963773215",
            ruimtelijk_object="",
        )

        url = reverse("plannen:subject-detail", kwargs={"uuid": subject.uuid})
        response = self.client.patch(
            url, {"ruimtelijk_object": "urn:example:object:123"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "ruimtelijkObject")
        self.assertEqual(error["reason"], self.PERSOON_RUIMTELIJK_OBJECT_ERROR)
        subject.refresh_from_db()
        self.assertEqual(subject.ruimtelijk_object, "")

    def test_partial_update_fysiek_object_add_bsn(self):
        subject = SubjectFactory.create(
            subjecttype=SubjectType.FYSIEK_OBJECT,
            ruimtelijk_object="urn:example:object:123",
            klant="",
            bsn="",
        )

        url = reverse("plannen:subject-detail", kwargs={"uuid": subject.uuid})
        response = self.client.patch(url, {"bsn": "963773215"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "bsn")
        self.assertEqual(error["reason"], self.FYSIEK_OBJECT_KLANT_BSN_ERROR)
        subject.refresh_from_db()
        self.assertEqual(subject.bsn, "")

    @patch.object(subjecten_create_counter, "add", wraps=subjecten_create_counter.add)
    def test_create_subject_increments_metric(self, mock_add: MagicMock):
        plan = PlanFactory.create()
        url = reverse("plannen:subject-list")
        data = {
            "planUuid": str(plan.uuid),
            "subjecttype": SubjectType.PERSOON,
            "persoonsprofiel": "urn:example:persoon:12345",
            "klant": "urn:example:klant:67890",
            "bsn": "963773215",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        mock_add.assert_called_once_with(1)

    @patch.object(subjecten_update_counter, "add", wraps=subjecten_update_counter.add)
    def test_update_subject_increments_metric(self, mock_add: MagicMock):
        subject = SubjectFactory.create()
        new_data = {"bsn": "111222333"}
        url = reverse("plannen:subject-detail", kwargs={"uuid": subject.uuid})
        response = self.client.patch(url, new_data, format="json")
        self.assertEqual(response.status_code, 200)
        mock_add.assert_called_once_with(1)

    @patch.object(subjecten_delete_counter, "add", wraps=subjecten_delete_counter.add)
    def test_delete_subject_increments_metric(self, mock_add: MagicMock):
        subject = SubjectFactory.create()
        url = reverse("plannen:subject-detail", kwargs={"uuid": subject.uuid})
        response = self.client.delete(url)
        self.assertIn(response.status_code, (200, 204))
        mock_add.assert_called_once_with(1)
