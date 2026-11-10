from datetime import date, datetime
from unittest.mock import MagicMock, patch

from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.test import APIClient
from vng_api_common.tests import get_validation_errors

from openplan.plannen.enums.status import Planstatus
from openplan.plannen.metrics import (
    plannen_create_counter,
    plannen_delete_counter,
    plannen_update_counter,
)
from openplan.plannen.models.factories.plan import PlanFactory

from ...models.plan import Plan
from .api_testcase import APITestCase


class PlanAPITests(APITestCase):
    DATUM_ERROR = _(
        "De einddatum mag niet op een eerdere of dezelfde dag vallen als de startdatum."
    )
    BEOOGDE_EINDDATUM_ERROR = _(
        "De beoogde_einddatum mag niet op een eerdere of dezelfde dag vallen "
        "als de beoogde_startdatum."
    )

    def setUp(self):
        super().setUp()
        self.data = {
            "naam": "Test Plan",
            "startdatum": date.today().isoformat(),
            "beoogde_startdatum": date.today().isoformat(),
        }

    def test_create_plan(self):
        url = reverse("plannen:plan-list")
        data = {
            "naam": "Test Instrument",
            "startdatum": date.today().isoformat(),
            "beoogde_startdatum": date.today().isoformat(),
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        plan = Plan.objects.get(uuid=response.data["uuid"])
        self.assertEqual(str(plan.uuid), response.data["uuid"])

    def test_list_plans(self):
        PlanFactory.create_batch(3)

        url = reverse("plannen:plan-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 3)

        for plan_data in data:
            self.assertIn("uuid", plan_data)

    def test_retrieve_plan(self):
        plan = PlanFactory.create()

        url = reverse("plannen:plan-detail", kwargs={"uuid": plan.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(plan.uuid))

    def test_update_plan(self):
        plan = PlanFactory.create()

        url = reverse("plannen:plan-detail", kwargs={"uuid": plan.uuid})
        data = {
            "naam": "Test update instrument",
            "startdatum": date.today().isoformat(),
            "beoogde_startdatum": date.today().isoformat(),
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        plan.refresh_from_db()
        self.assertEqual(plan.naam, "Test update instrument")

    def test_partial_update_plan(self):
        plan = PlanFactory.create()

        url = reverse("plannen:plan-detail", kwargs={"uuid": plan.uuid})
        data = {"naam": "Test update instrument"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        plan.refresh_from_db()
        self.assertEqual(plan.naam, "Test update instrument")

    def test_delete_plan(self):
        plan = PlanFactory.create()

        url = reverse("plannen:plan-detail", kwargs={"uuid": plan.uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Plan.objects.filter(uuid=plan.uuid).exists())

    def test_create_plan_with_valid_einddatums(self):
        url = reverse("plannen:plan-list")
        data = {
            **self.data,
            "startdatum": "2026-01-10",
            "einddatum": "2026-01-20",
            "beoogde_startdatum": "2026-01-10",
            "beoogde_einddatum": "2026-01-20",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_plan_einddatum_before_startdatum(self):
        url = reverse("plannen:plan-list")
        data = {
            **self.data,
            "startdatum": "2026-01-10",
            "einddatum": "2026-01-05",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "einddatum")
        self.assertEqual(error["reason"], self.DATUM_ERROR)
        self.assertFalse(Plan.objects.exists())

    def test_create_plan_einddatum_same_as_startdatum(self):
        url = reverse("plannen:plan-list")
        data = {
            **self.data,
            "startdatum": "2026-01-10",
            "einddatum": "2026-01-10",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "einddatum")
        self.assertEqual(error["reason"], self.DATUM_ERROR)

    def test_create_plan_beoogde_einddatum_before_beoogde_startdatum(self):
        url = reverse("plannen:plan-list")
        data = {
            **self.data,
            "beoogde_startdatum": "2026-01-10",
            "beoogde_einddatum": "2026-01-05",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "beoogdeEinddatum")
        self.assertEqual(error["reason"], self.BEOOGDE_EINDDATUM_ERROR)
        self.assertFalse(Plan.objects.exists())

    def test_partial_update_plan_einddatum_before_existing_startdatum(self):
        plan = PlanFactory.create(startdatum=date(2026, 1, 10), einddatum=None)

        url = reverse("plannen:plan-detail", kwargs={"uuid": plan.uuid})
        response = self.client.patch(url, {"einddatum": "2026-01-05"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "einddatum")
        self.assertEqual(error["reason"], self.DATUM_ERROR)
        plan.refresh_from_db()
        self.assertIsNone(plan.einddatum)

    def test_partial_update_plan_startdatum_after_existing_einddatum(self):
        plan = PlanFactory.create(
            startdatum=date(2026, 1, 10), einddatum=date(2026, 1, 20)
        )

        url = reverse("plannen:plan-detail", kwargs={"uuid": plan.uuid})
        response = self.client.patch(url, {"startdatum": "2026-01-25"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "einddatum")
        self.assertEqual(error["reason"], self.DATUM_ERROR)
        plan.refresh_from_db()
        self.assertEqual(plan.startdatum, date(2026, 1, 10))

    def test_partial_update_plan_valid_einddatum(self):
        plan = PlanFactory.create(
            startdatum=date(2026, 1, 10),
            einddatum=None,
            beoogde_startdatum=date(2026, 1, 10),
            beoogde_einddatum=None,
        )

        url = reverse("plannen:plan-detail", kwargs={"uuid": plan.uuid})
        response = self.client.patch(url, {"einddatum": "2026-01-20"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        plan.refresh_from_db()
        self.assertEqual(plan.einddatum, date(2026, 1, 20))

    def test_authentication_required(self):
        client = APIClient()
        url = reverse("plannen:plan-list")

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_status(self):
        plan1 = PlanFactory.create(status=Planstatus.CONCEPT)
        PlanFactory.create(status=Planstatus.VASTGESTELD)

        url = reverse("plannen:plan-list")
        response = self.client.get(url, {"status": "concept"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(plan1.uuid))

    def test_filter_naam(self):
        plan1 = PlanFactory.create(naam="Project Start")
        PlanFactory.create(naam="Project End")

        url = reverse("plannen:plan-list")
        with self.subTest("exact"):
            response = self.client.get(url, {"naam": "Project Start"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["uuid"], str(plan1.uuid))

        with self.subTest("icontains"):
            response = self.client.get(url, {"naam__icontains": "Start"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["uuid"], str(plan1.uuid))

    def test_filter_eigenaar(self):
        plan1 = PlanFactory.create(eigenaar="urn:example:persoon:1")
        PlanFactory.create(eigenaar="urn:example:persoon:2")

        url = reverse("plannen:plan-list")
        response = self.client.get(url, {"eigenaar": "urn:example:persoon:1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(plan1.uuid))

    def test_filter_zaak(self):
        plan1 = PlanFactory.create(zaak="urn:example:zaak:1")
        PlanFactory.create(zaak="urn:example:zaak:2")

        url = reverse("plannen:plan-list")
        response = self.client.get(url, {"zaak": "urn:example:zaak:1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(plan1.uuid))

    def test_filter_contactmoment(self):
        plan1 = PlanFactory.create(contactmoment="urn:example:contactmoment:1")
        PlanFactory.create(contactmoment="urn:example:contactmoment:2")

        url = reverse("plannen:plan-list")
        response = self.client.get(
            url, {"contactmoment": "urn:example:contactmoment:1"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(plan1.uuid))

    def test_startdatum_filter(self):
        plan1 = PlanFactory.create(startdatum=timezone.make_aware(datetime(2026, 1, 1)))
        PlanFactory.create(startdatum=timezone.make_aware(datetime(2026, 2, 1)))

        url = reverse("plannen:plan-list")
        with self.subTest("exact"):
            response = self.client.get(url, {"startdatum": "2026-01-01"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["uuid"], str(plan1.uuid))

        with self.subTest("lte"):
            response = self.client.get(url, {"startdatum__lte": "2026-01-31"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("gte"):
            response = self.client.get(url, {"startdatum__gte": "2026-02-01"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    def test_einddatum_filter(self):
        plan1 = PlanFactory.create(
            startdatum=timezone.make_aware(datetime(2026, 1, 1)),
            einddatum=timezone.make_aware(datetime(2026, 1, 15)),
        )
        PlanFactory.create(
            startdatum=timezone.make_aware(datetime(2026, 2, 1)),
            einddatum=timezone.make_aware(datetime(2026, 2, 15)),
        )

        url = reverse("plannen:plan-list")
        with self.subTest("exact"):
            response = self.client.get(url, {"einddatum": "2026-01-15"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)
            self.assertEqual(response.data["results"][0]["uuid"], str(plan1.uuid))

        with self.subTest("lte"):
            response = self.client.get(url, {"einddatum__lte": "2026-01-31"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("gte"):
            response = self.client.get(url, {"einddatum__gte": "2026-02-01"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

    def test_plan_urn(self):
        plan = PlanFactory.create()

        url = reverse("plannen:plan-detail", kwargs={"uuid": plan.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["urn"], f"urn:maykin:plannen:plan:{str(plan.uuid)}"
        )

    def test_invalid_create_urn_fields_plan(self):
        self.assertFalse(Plan.objects.exists())

        data = {
            "naam": "Test Plan",
            "zaak": "invalid",
            "contactmoment": "urn:maykinmaykinmaykinmaykinmaykinmaykinmaykinmaykinmaykin:1",
            "eigenaar": "test:maykin:organisatie:medewerker:1234567892",
        }

        url = reverse("plannen:plan-list")
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            get_validation_errors(response, "zaak"),
            {
                "name": "zaak",
                "code": "invalid_urn",
                "reason": "Enter a valid URN. Correct format: 'urn:<namespace>:<resource>' (e.g., urn:isbn:9780143127796).",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "contactmoment"),
            {
                "name": "contactmoment",
                "code": "invalid_urn",
                "reason": "Enter a valid URN. Correct format: 'urn:<namespace>:<resource>' (e.g., urn:isbn:9780143127796).",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "eigenaar"),
            {
                "name": "eigenaar",
                "code": "invalid_urn",
                "reason": "Enter a valid URN. Correct format: 'urn:<namespace>:<resource>' (e.g., urn:isbn:9780143127796).",
            },
        )
        self.assertFalse(Plan.objects.exists())

    @patch.object(plannen_create_counter, "add", wraps=plannen_create_counter.add)
    def test_create_plan_increments_metric(self, mock_add: MagicMock):
        url = reverse("plannen:plan-list")
        data = {
            "naam": "Test Instrument",
            "startdatum": date.today().isoformat(),
            "beoogde_startdatum": date.today().isoformat(),
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        mock_add.assert_called_once_with(1)

    @patch.object(plannen_update_counter, "add", wraps=plannen_update_counter.add)
    def test_update_plan_increments_metric(self, mock_add: MagicMock):
        plan = PlanFactory.create()
        url = reverse("plannen:plan-detail", kwargs={"uuid": plan.uuid})
        data = {"naam": "Updated Plan"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        mock_add.assert_called_once_with(1)

    @patch.object(plannen_delete_counter, "add", wraps=plannen_delete_counter.add)
    def test_delete_plan_increments_metric(self, mock_add: MagicMock):
        plan = PlanFactory.create()
        url = reverse("plannen:plan-detail", kwargs={"uuid": plan.uuid})
        response = self.client.delete(url)
        self.assertIn(response.status_code, (200, 204))
        mock_add.assert_called_once_with(1)
