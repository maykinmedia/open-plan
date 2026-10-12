from datetime import date

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from openplan.plannen.enums.status import PlanStatus
from openplan.plannen.models.factories.evaluatie import (
    EvaluatieFactory,
    EvaluatieTypeFactory,
)
from openplan.plannen.models.factories.plan import PlanFactory

from ...models.evaluatie import Evaluatie
from .api_testcase import APITestCase


class EvaluatieAPITests(APITestCase):
    def setUp(self):
        super().setUp()
        self.plan = PlanFactory.create()
        self.other_plan = PlanFactory.create()

    # TODO: Fix tests after evaluatie type api is set up
    def test_create_evaluatie(self):
        evaluatietype = EvaluatieTypeFactory.create()
        plan = PlanFactory.create()
        url = reverse("plannen:evaluatie-list")
        data = {
            "evaluatie_type": str(evaluatietype.uuid),
            "plan_uuid": str(plan.uuid),
            "datum": str(date.today()),
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        evaluatie = Evaluatie.objects.get(uuid=response.data["uuid"])
        self.assertEqual(evaluatie.plan, plan)

    def test_list_evaluaties(self):
        EvaluatieFactory.create_batch(3)

        url = reverse("plannen:evaluatie-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 3)
        for cm in data:
            self.assertIn("uuid", cm)
            self.assertIn("plan", cm)

    def test_retrieve_evaluatie(self):
        evaluatie = EvaluatieFactory.create()
        url = reverse("plannen:evaluatie-detail", kwargs={"uuid": evaluatie.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(evaluatie.uuid))
        self.assertEqual(response.data["plan"]["uuid"], str(evaluatie.plan.uuid))

    def test_update_evaluatie(self):
        evaluatietype = EvaluatieTypeFactory.create()
        evaluatie = EvaluatieFactory.create()
        new_plan = PlanFactory.create()

        url = reverse("plannen:evaluatie-detail", kwargs={"uuid": evaluatie.uuid})
        data = {
            "evaluatie_type": str(evaluatietype.uuid),
            "plan_uuid": str(new_plan.uuid),
            "datum": str(date.today()),
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        evaluatie.refresh_from_db()
        self.assertEqual(evaluatie.plan, new_plan)

    def test_partial_update_evaluatie(self):
        evaluatie = EvaluatieFactory.create()
        new_plan = PlanFactory.create()

        url = reverse("plannen:evaluatie-detail", kwargs={"uuid": evaluatie.uuid})
        data = {
            "plan_uuid": str(new_plan.uuid),
            "datum": str(date.today()),
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        evaluatie.refresh_from_db()
        self.assertEqual(evaluatie.plan, new_plan)

    def test_delete_evaluatie(self):
        evaluatie = EvaluatieFactory.create()
        url = reverse("plannen:evaluatie-detail", kwargs={"uuid": evaluatie.uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Evaluatie.objects.filter(uuid=evaluatie.uuid).exists())

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:evaluatie-list")
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_plan_uuid(self):
        evaluatie1 = EvaluatieFactory.create(plan=self.plan)
        EvaluatieFactory.create(plan=self.other_plan)

        url = reverse("plannen:evaluatie-list")
        response = self.client.get(url, {"plan__uuid": str(self.plan.uuid)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(evaluatie1.uuid))

    def test_filter_by_status(self):
        evaluatie1 = EvaluatieFactory.create(status=PlanStatus.ACTIEF)
        EvaluatieFactory.create(status=PlanStatus.AFGEROND)

        url = reverse("plannen:evaluatie-list")
        response = self.client.get(url, {"status": "actief"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(evaluatie1.uuid))

    def test_filter_datum(self):
        EvaluatieFactory.create(datum="2024-06-07T00:00:00Z")
        EvaluatieFactory.create(datum="2025-06-07T00:00:00Z")

        url = reverse("plannen:evaluatie-list")

        with self.subTest("exact"):
            response = self.client.get(url, {"datum": "2024-06-07T00:00:00Z"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("lte"):
            response = self.client.get(url, {"datum__lte": "2024-07-07T00:00:00Z"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("gte"):
            response = self.client.get(url, {"datum__gte": "2025-04-07T00:00:00Z"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["count"], 1)

    # @patch.object(
    #     contactmomenten_create_counter, "add", wraps=contactmomenten_create_counter.add
    # )
    # def test_create_evaluatie_increments_metric(self, mock_add: MagicMock):
    #     plan = PlanFactory.create()
    #     url = reverse("plannen:evaluatie-list")
    #     data = {
    #         "plan_uuid": str(plan.uuid),
    #         "datum": str(date.today()),
    #     }
    #     response = self.client.post(url, data, format="json")
    #     self.assertEqual(response.status_code, 201)
    #     mock_add.assert_called_once_with(1)

    # @patch.object(
    #     contactmomenten_update_counter, "add", wraps=contactmomenten_update_counter.add
    # )
    # def test_update_evaluatie_increments_metric(self, mock_add: MagicMock):
    #     evaluatie = EvaluatieFactory.create()
    #     new_plan = PlanFactory.create()
    #     url = reverse("plannen:evaluatie-detail", kwargs={"uuid": evaluatie.uuid})
    #     data = {
    #         "plan_uuid": str(new_plan.uuid),
    #         "datum": str(date.today()),
    #     }
    #     response = self.client.put(url, data, format="json")
    #     self.assertEqual(response.status_code, 200)
    #     mock_add.assert_called_once_with(1)

    # @patch.object(
    #     contactmomenten_delete_counter, "add", wraps=contactmomenten_delete_counter.add
    # )
    # def test_delete_evaluatie_increments_metric(self, mock_add: MagicMock):
    #     evaluatie = EvaluatieFactory.create()
    #     url = reverse("plannen:evaluatie-detail", kwargs={"uuid": evaluatie.uuid})
    #     response = self.client.delete(url)
    #     self.assertIn(response.status_code, (200, 204))
    #     mock_add.assert_called_once_with(1)
