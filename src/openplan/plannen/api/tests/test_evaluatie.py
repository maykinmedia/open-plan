import uuid
from datetime import date
from unittest.mock import MagicMock, patch

from django.db.models import ProtectedError
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from vng_api_common.tests import get_validation_errors

from openplan.plannen.enums.status import DoelStatus
from openplan.plannen.metrics import (
    evaluatie_create_counter,
    evaluatie_delete_counter,
    evaluatie_update_counter,
)
from openplan.plannen.models.factories.doel import DoelFactory
from openplan.plannen.models.factories.evaluatie import (
    EvaluatieFactory,
    EvaluatieTypeFactory,
)
from openplan.plannen.models.factories.plan import PlanFactory
from openplan.plannen.models.factories.positie import PositieFactory
from openplan.plannen.models.factories.subdoel import SubdoelFactory

from ...models.evaluatie import Evaluatie
from .api_testcase import APITestCase


class EvaluatieAPITests(APITestCase):
    def setUp(self):
        super().setUp()
        self.plan = PlanFactory.create()
        self.other_plan = PlanFactory.create()

    def test_create_evaluatie(self):
        evaluatietype = EvaluatieTypeFactory.create()
        plan = PlanFactory.create()
        url = reverse("plannen:evaluatie-list")
        data = {
            "evaluatietype_uuid": str(evaluatietype.uuid),
            "plan_uuid": str(plan.uuid),
            "naam": "Eerste evaluatie",
            "datum": date.today().isoformat(),
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        evaluatie = Evaluatie.objects.get(uuid=response.data["uuid"])
        self.assertEqual(evaluatie.plan, plan)
        self.assertEqual(evaluatie.evaluatietype, evaluatietype)
        self.assertEqual(evaluatie.naam, "Eerste evaluatie")
        self.assertEqual(evaluatie.status, DoelStatus.GEPLAND)

    def test_create_evaluatie_missing_required_fields(self):
        url = reverse("plannen:evaluatie-list")
        data = {
            "plan_uuid": str(self.plan.uuid),
            "datum": date.today().isoformat(),
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("evaluatietypeUuid", "naam"):
            with self.subTest(field=field):
                error = get_validation_errors(response, field)
                self.assertIsNotNone(error)
                self.assertEqual(error["code"], "required")

    def test_list_evaluaties(self):
        EvaluatieFactory.create_batch(3)

        url = reverse("plannen:evaluatie-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        self.assertEqual(len(data), 3)
        for item in data:
            self.assertIn("uuid", item)
            self.assertIn("plan", item)
            self.assertIn("naam", item)
            # TODO: check evaluatietype once the evaluatietype api is implemented

    def test_retrieve_evaluatie(self):
        evaluatie = EvaluatieFactory.create()
        url = reverse("plannen:evaluatie-detail", kwargs={"uuid": evaluatie.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(evaluatie.uuid))
        self.assertEqual(response.data["plan"]["uuid"], str(evaluatie.plan.uuid))
        self.assertEqual(response.data["naam"], evaluatie.naam)
        self.assertEqual(response.data["status"], DoelStatus.GEPLAND)
        # TODO: check evaluatietype once the evaluatietype api is implemented

    def test_update_evaluatie(self):
        evaluatietype = EvaluatieTypeFactory.create()
        evaluatie = EvaluatieFactory.create()
        new_plan = PlanFactory.create()

        url = reverse("plannen:evaluatie-detail", kwargs={"uuid": evaluatie.uuid})
        data = {
            "evaluatietype_uuid": str(evaluatietype.uuid),
            "plan_uuid": str(new_plan.uuid),
            "naam": "Bijgewerkte evaluatie",
            "datum": date.today().isoformat(),
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        evaluatie.refresh_from_db()
        self.assertEqual(evaluatie.plan, new_plan)
        self.assertEqual(evaluatie.evaluatietype, evaluatietype)
        self.assertEqual(evaluatie.naam, "Bijgewerkte evaluatie")

    def test_partial_update_evaluatie(self):
        evaluatie = EvaluatieFactory.create()
        new_plan = PlanFactory.create()

        url = reverse("plannen:evaluatie-detail", kwargs={"uuid": evaluatie.uuid})
        data = {
            "plan_uuid": str(new_plan.uuid),
            "datum": date.today().isoformat(),
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

    def test_delete_evaluatietype_in_use_is_protected(self):
        # Evaluatie.evaluatietype uses on_delete=PROTECT
        evaluatie = EvaluatieFactory.create()
        with self.assertRaises(ProtectedError):
            evaluatie.evaluatietype.delete()

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
        other_status = next(s for s in DoelStatus if s != DoelStatus.GEPLAND)
        evaluatie1 = EvaluatieFactory.create(status=DoelStatus.GEPLAND)
        EvaluatieFactory.create(status=other_status)

        url = reverse("plannen:evaluatie-list")
        response = self.client.get(url, {"status": DoelStatus.GEPLAND.value})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["uuid"], str(evaluatie1.uuid))

    def test_filter_datum(self):
        EvaluatieFactory.create(datum="2024-06-07")
        EvaluatieFactory.create(datum="2025-06-07")

        url = reverse("plannen:evaluatie-list")

        with self.subTest("exact"):
            response = self.client.get(url, {"datum": "2024-06-07"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("lte"):
            response = self.client.get(url, {"datum__lte": "2024-07-07"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["count"], 1)

        with self.subTest("gte"):
            response = self.client.get(url, {"datum__gte": "2025-04-07"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["count"], 1)

    @patch.object(evaluatie_create_counter, "add", wraps=evaluatie_create_counter.add)
    def test_create_evaluatie_increments_metric(self, mock_add: MagicMock):
        evaluatietype = EvaluatieTypeFactory.create()
        url = reverse("plannen:evaluatie-list")
        data = {
            "plan_uuid": str(self.plan.uuid),
            "evaluatietype_uuid": str(evaluatietype.uuid),
            "naam": "Evaluatie metric",
            "datum": date.today().isoformat(),
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_add.assert_called_once_with(1)

    @patch.object(evaluatie_update_counter, "add", wraps=evaluatie_update_counter.add)
    def test_update_evaluatie_increments_metric(self, mock_add: MagicMock):
        evaluatie = EvaluatieFactory.create()
        evaluatietype = EvaluatieTypeFactory.create()
        url = reverse("plannen:evaluatie-detail", kwargs={"uuid": evaluatie.uuid})
        data = {
            "plan_uuid": str(self.other_plan.uuid),
            "evaluatietype_uuid": str(evaluatietype.uuid),
            "naam": "Bijgewerkte evaluatie metric",
            "datum": date.today().isoformat(),
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_add.assert_called_once_with(1)

    @patch.object(evaluatie_delete_counter, "add", wraps=evaluatie_delete_counter.add)
    def test_delete_evaluatie_increments_metric(self, mock_add: MagicMock):
        evaluatie = EvaluatieFactory.create()
        url = reverse("plannen:evaluatie-detail", kwargs={"uuid": evaluatie.uuid})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_add.assert_called_once_with(1)


class EvaluatieRelatiesAPITests(APITestCase):
    def setUp(self):
        super().setUp()
        self.plan = PlanFactory.create()
        self.evaluatietype = EvaluatieTypeFactory.create()
        self.list_url = reverse("plannen:evaluatie-list")

    def _base_data(self, **extra):
        data = {
            "plan_uuid": str(self.plan.uuid),
            "evaluatietype_uuid": str(self.evaluatietype.uuid),
            "naam": "Evaluatie met relaties",
            "datum": date.today().isoformat(),
        }
        data.update(extra)
        return data

    def _detail_url(self, evaluatie):
        return reverse("plannen:evaluatie-detail", kwargs={"uuid": evaluatie.uuid})

    def test_uuid_fields_are_write_only(self):
        evaluatie = EvaluatieFactory.create()

        response = self.client.get(self._detail_url(evaluatie))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        for field in (
            "evaluatietypeUuid",
            "positieUuids",
            "doelUuids",
            "subdoelUuids",
        ):
            with self.subTest(field=field):
                self.assertNotIn(field, body)

    def test_create_with_unknown_evaluatietype_uuid(self):
        data = self._base_data(evaluatietype_uuid=str(uuid.uuid4()))

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(get_validation_errors(response, "evaluatietypeUuid"))
        self.assertFalse(Evaluatie.objects.exists())

    def test_create_with_invalid_evaluatietype_uuid_format(self):
        data = self._base_data(evaluatietype_uuid="geen-uuid")

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(get_validation_errors(response, "evaluatietypeUuid"))

    def test_partial_update_evaluatietype(self):
        evaluatie = EvaluatieFactory.create()
        new_type = EvaluatieTypeFactory.create()

        response = self.client.patch(
            self._detail_url(evaluatie),
            {"evaluatietype_uuid": str(new_type.uuid)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        evaluatie.refresh_from_db()
        self.assertEqual(evaluatie.evaluatietype, new_type)

    def test_create_without_relations(self):
        response = self.client.post(self.list_url, self._base_data(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["doelen"], [])
        evaluatie = Evaluatie.objects.get(uuid=response.data["uuid"])
        self.assertFalse(evaluatie.posities.exists())
        self.assertFalse(evaluatie.doelen.exists())
        self.assertFalse(evaluatie.subdoelen.exists())

    def test_create_with_relations(self):
        posities = PositieFactory.create_batch(2)
        doelen = DoelFactory.create_batch(2)
        subdoelen = SubdoelFactory.create_batch(2)
        data = self._base_data(
            positie_uuids=[str(p.uuid) for p in posities],
            doel_uuids=[str(d.uuid) for d in doelen],
            subdoel_uuids=[str(s.uuid) for s in subdoelen],
        )

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        evaluatie = Evaluatie.objects.get(uuid=response.data["uuid"])
        self.assertEqual(set(evaluatie.posities.all()), set(posities))
        self.assertEqual(set(evaluatie.doelen.all()), set(doelen))
        self.assertEqual(set(evaluatie.subdoelen.all()), set(subdoelen))

        # doelen is returned nested
        self.assertEqual(
            {str(d["uuid"]) for d in response.data["doelen"]},
            {str(d.uuid) for d in doelen},
        )

    def test_retrieve_shows_nested_doelen(self):
        evaluatie = EvaluatieFactory.create()
        doel = DoelFactory.create()
        evaluatie.doelen.add(doel)

        response = self.client.get(self._detail_url(evaluatie))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["doelen"]), 1)
        self.assertEqual(str(response.data["doelen"][0]["uuid"]), str(doel.uuid))
        # TODO: check posities and subdoelen once their nested serializers exist

    def test_update_replaces_relations(self):
        evaluatie = EvaluatieFactory.create()
        evaluatie.posities.add(PositieFactory.create())
        evaluatie.doelen.add(DoelFactory.create())
        evaluatie.subdoelen.add(SubdoelFactory.create())
        new_positie = PositieFactory.create()
        new_doel = DoelFactory.create()
        new_subdoel = SubdoelFactory.create()

        response = self.client.put(
            self._detail_url(evaluatie),
            self._base_data(
                positie_uuids=[str(new_positie.uuid)],
                doel_uuids=[str(new_doel.uuid)],
                subdoel_uuids=[str(new_subdoel.uuid)],
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(evaluatie.posities.all()), [new_positie])
        self.assertEqual(list(evaluatie.doelen.all()), [new_doel])
        self.assertEqual(list(evaluatie.subdoelen.all()), [new_subdoel])

    def test_partial_update_clears_relations(self):
        evaluatie = EvaluatieFactory.create()
        evaluatie.posities.add(PositieFactory.create())
        evaluatie.doelen.add(DoelFactory.create())
        evaluatie.subdoelen.add(SubdoelFactory.create())

        response = self.client.patch(
            self._detail_url(evaluatie),
            {"positie_uuids": [], "doel_uuids": [], "subdoel_uuids": []},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(evaluatie.posities.exists())
        self.assertFalse(evaluatie.doelen.exists())
        self.assertFalse(evaluatie.subdoelen.exists())

    def test_partial_update_without_relations_keeps_them(self):
        evaluatie = EvaluatieFactory.create()
        positie = PositieFactory.create()
        doel = DoelFactory.create()
        subdoel = SubdoelFactory.create()
        evaluatie.posities.add(positie)
        evaluatie.doelen.add(doel)
        evaluatie.subdoelen.add(subdoel)

        response = self.client.patch(
            self._detail_url(evaluatie), {"naam": "Andere naam"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(evaluatie.posities.all()), [positie])
        self.assertEqual(list(evaluatie.doelen.all()), [doel])
        self.assertEqual(list(evaluatie.subdoelen.all()), [subdoel])
