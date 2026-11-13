from datetime import date

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.test import APIClient
from vng_api_common.tests import get_validation_errors

from openplan.plannen.enums.status import RedenWijziging
from openplan.plannen.models.factories.doel import DoelFactory
from openplan.plannen.models.factories.doeltype import DoelTypeFactory
from openplan.plannen.models.factories.positie import PositieFactory

from ...models.doel import Doel
from .api_testcase import APITestCase

ANDERE_REDEN = next(
    reden for reden in RedenWijziging.values if reden != RedenWijziging.REGISTREREN
)


class DoelHistoryAPITests(APITestCase):
    REDEN_VERPLICHT_ERROR = _("Een reden is verplicht bij wijzigen.")

    def setUp(self):
        super().setUp()
        self.hoofddoel_type = DoelTypeFactory.create(naam="hoofddoel")
        self.positie = PositieFactory.create()

        self.data = {
            "doeltypeUuid": str(self.hoofddoel_type.uuid),
            "positieUuid": str(self.positie.uuid),
            "naam": "Test Doel",
            "startdatum": str(date.today()),
            "beoogde_startdatum": date.today().isoformat(),
            "omschrijving": "Beschrijving test",
        }

    def _update_data(self, doel, **extra):
        return {
            "positieUuid": str(doel.positie.uuid),
            "naam": "Test update Doel",
            "startdatum": str(date.today()),
            "beoogde_startdatum": date.today().isoformat(),
            "omschrijving": "Beschrijving update test",
            **extra,
        }

    def test_create_doel_history_registreren(self):
        url = reverse("plannen:doel-list")
        response = self.client.post(url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doel = Doel.objects.get(uuid=response.data["uuid"])
        self.assertEqual(doel.history.count(), 1)

        record = doel.history.get()
        self.assertEqual(record.history_type, "+")
        self.assertEqual(record.reden_wijziging, RedenWijziging.REGISTREREN)
        self.assertEqual(record.toelichting_reden, "")

    def test_create_doel_ignores_reden_wijziging(self):
        url = reverse("plannen:doel-list")
        data = {
            **self.data,
            "redenWijziging": ANDERE_REDEN,
            "toelichtingReden": "Niet nodig",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        record = Doel.objects.get(uuid=response.data["uuid"]).history.get()
        self.assertEqual(record.reden_wijziging, RedenWijziging.REGISTREREN)
        self.assertEqual(record.toelichting_reden, "")

    def test_factory_doel_history_registreren(self):
        doel = DoelFactory.create()

        record = doel.history.get()
        self.assertEqual(record.history_type, "+")
        self.assertEqual(record.reden_wijziging, RedenWijziging.REGISTREREN)

    def test_update_doel_without_reden_returns_400(self):
        doel = DoelFactory.create(naam="Origineel")

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        response = self.client.put(url, self._update_data(doel), format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "redenWijziging")
        self.assertEqual(error["reason"], self.REDEN_VERPLICHT_ERROR)

        doel.refresh_from_db()
        self.assertEqual(doel.naam, "Origineel")
        self.assertEqual(doel.history.count(), 1)

    def test_partial_update_doel_without_reden_returns_400(self):
        doel = DoelFactory.create(naam="Origineel")

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        response = self.client.patch(url, {"naam": "Gewijzigd"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "redenWijziging")
        self.assertEqual(error["reason"], self.REDEN_VERPLICHT_ERROR)

        doel.refresh_from_db()
        self.assertEqual(doel.naam, "Origineel")
        self.assertEqual(doel.history.count(), 1)

    def test_partial_update_doel_empty_reden_returns_400(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        response = self.client.patch(
            url, {"naam": "Gewijzigd", "redenWijziging": ""}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        get_validation_errors(response, "redenWijziging")
        self.assertEqual(doel.history.count(), 1)

    def test_partial_update_doel_invalid_reden_returns_400(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        response = self.client.patch(
            url, {"naam": "Gewijzigd", "redenWijziging": "bestaat_niet"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        get_validation_errors(response, "redenWijziging")
        self.assertEqual(doel.history.count(), 1)

    def test_update_doel_stores_reden_in_history(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        data = self._update_data(
            doel,
            redenWijziging=ANDERE_REDEN,
            toelichtingReden="Beschrijving aangepast",
        )
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(doel.history.count(), 2)

        record = doel.history.latest()
        self.assertEqual(record.history_type, "~")
        self.assertEqual(record.naam, "Test update Doel")
        self.assertEqual(record.reden_wijziging, ANDERE_REDEN)
        self.assertEqual(record.toelichting_reden, "Beschrijving aangepast")

    def test_partial_update_doel_stores_reden_in_history(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        data = {
            "naam": "New titel",
            "redenWijziging": ANDERE_REDEN,
            "toelichtingReden": "Typfout in naam",
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doel.refresh_from_db()
        self.assertEqual(doel.naam, "New titel")

        record = doel.history.latest()
        self.assertEqual(record.history_type, "~")
        self.assertEqual(record.reden_wijziging, ANDERE_REDEN)
        self.assertEqual(record.toelichting_reden, "Typfout in naam")

    def test_partial_update_doel_toelichting_optional(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        data = {"naam": "New titel", "redenWijziging": ANDERE_REDEN}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(doel.history.latest().toelichting_reden, "")

    def test_reden_not_in_doel_response(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        data = {"naam": "New titel", "redenWijziging": ANDERE_REDEN}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("redenWijziging", response.json())
        self.assertNotIn("toelichtingReden", response.json())

        response = self.client.get(url)
        self.assertNotIn("redenWijziging", response.json())

    def test_reden_only_used_for_one_save(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        data = {"naam": "New titel", "redenWijziging": ANDERE_REDEN}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        doel = Doel.objects.get(uuid=doel.uuid)
        doel.omschrijving = "Aangepast in code"
        doel.save()

        self.assertEqual(doel.history.latest().reden_wijziging, "")

    def test_list_history(self):
        doel = DoelFactory.create(naam="Origineel")

        detail_url = reverse("plannen:doel-detail", kwargs={"uuid": doel.uuid})
        data = {
            "naam": "Gewijzigd",
            "redenWijziging": ANDERE_REDEN,
            "toelichtingReden": "Typfout",
        }
        response = self.client.patch(detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse("plannen:doel-history", kwargs={"uuid": doel.uuid})
        response = self.client.get(url)
        print("TIMMM", response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        nieuwste, oudste = response.json()["results"]
        self.assertEqual(nieuwste["historyType"], "~")
        self.assertEqual(nieuwste["naam"], "Gewijzigd")
        self.assertEqual(nieuwste["redenWijziging"], ANDERE_REDEN)
        self.assertEqual(nieuwste["toelichtingReden"], "Typfout")

        self.assertEqual(oudste["historyType"], "+")
        self.assertEqual(oudste["naam"], "Origineel")
        self.assertEqual(oudste["redenWijziging"], RedenWijziging.REGISTREREN)

    def test_list_history_fields(self):
        doel = DoelFactory.create()

        url = reverse("plannen:doel-history", kwargs={"uuid": doel.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        record = response.json()["results"][0]
        for veld in (
            "historyId",
            "historyDate",
            "historyType",
            "historyUser",
            "redenWijziging",
            "toelichtingReden",
            "uuid",
            "naam",
        ):
            with self.subTest(veld=veld):
                self.assertIn(veld, record)
        self.assertNotIn("historyChangeReason", record)

    def test_list_history_only_own_doel(self):
        doel = DoelFactory.create(naam="Eigen doel")
        DoelFactory.create(naam="Ander doel")

        url = reverse("plannen:doel-history", kwargs={"uuid": doel.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["naam"], "Eigen doel")

    def test_list_history_unknown_doel_returns_404(self):
        url = reverse(
            "plannen:doel-history",
            kwargs={"uuid": "00000000-0000-0000-0000-000000000000"},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_history(self):
        doel = DoelFactory.create(naam="Origineel")
        record = doel.history.get()

        url = reverse(
            "plannen:doel-history-detail",
            kwargs={"uuid": doel.uuid, "history_id": record.history_id},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["history_id"], record.history_id)
        self.assertEqual(response.data["naam"], "Origineel")
        self.assertEqual(response.data["reden_wijziging"], RedenWijziging.REGISTREREN)

    def test_retrieve_history_of_other_doel_returns_404(self):
        doel = DoelFactory.create()
        ander_record = DoelFactory.create().history.get()

        url = reverse(
            "plannen:doel-history-detail",
            kwargs={"uuid": doel.uuid, "history_id": ander_record.history_id},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_history_unknown_id_returns_404(self):
        doel = DoelFactory.create()

        url = reverse(
            "plannen:doel-history-detail",
            kwargs={"uuid": doel.uuid, "history_id": 999999},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_history_authentication_required(self):
        doel = DoelFactory.create()
        url = reverse("plannen:doel-history", kwargs={"uuid": doel.uuid})

        response = APIClient().get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
