from collections.abc import Callable
from typing import Any, TypedDict

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from openplan.plannen.models.factories.configuratie import ConfiguratieFactory
from openplan.plannen.models.factories.doel import DoelFactory
from openplan.plannen.models.factories.positie import PositieFactory
from openplan.plannen.models.factories.positietype import PositieTypeFactory

from ...models import Positie, PositieType
from .api_testcase import APITestCase


class Page(TypedDict):
    count: int
    next: str | None
    previous: str | None
    results: list[dict[str, Any]]


class ListQueryCountTests(APITestCase):
    """For one row shape a list costs a + b·rows queries, so two lengths give b.
    The rows fill every optional relation: an empty one costs no query."""

    def assert_no_query_per_row(
        self, url_name: str, add_row: Callable[[], object]
    ) -> None:
        url = reverse(f"plannen:{url_name}-list")
        add_row()
        with CaptureQueriesContext(connection) as before:
            self.client.get(url)
        add_row()
        with CaptureQueriesContext(connection) as after:
            self.client.get(url)

        self.assertEqual(
            len(after),
            len(before),
            f"{len(before)} queries, {len(after)} with a row more",
        )

    def test_positie_list(self) -> None:
        self.assert_no_query_per_row("positie", PositieFactory.create)

    def test_positietype_list(self) -> None:
        doelpositie = PositieTypeFactory.create()
        configuratie = ConfiguratieFactory.create()

        def add_positietype() -> None:
            positietype = PositieTypeFactory.create(doelpositie=doelpositie)
            positietype.configuraties.add(configuratie)

        self.assert_no_query_per_row("positietype", add_positietype)

    def test_doel_list(self) -> None:
        self.assert_no_query_per_row("doel", DoelFactory.create)

    def test_doeltype_list(self) -> None:
        configuratie = ConfiguratieFactory.create()

        def add_doeltype() -> None:
            doeltype = PositieTypeFactory.create()
            doeltype.configuraties.add(configuratie)

        self.assert_no_query_per_row("positietype", add_doeltype)


def uuids(model: type[Positie] | type[PositieType]) -> list[str]:
    return [str(uuid) for uuid in model.objects.values_list("uuid", flat=True)]


class PagingTests(APITestCase):
    def page(self, url_name: str, number: int) -> list[str]:
        body: Page = self.client.get(
            reverse(f"plannen:{url_name}-list"), {"pageSize": 1, "page": number}
        ).json()
        return [row["uuid"] for row in body["results"]]

    def assert_edit_keeps_rows_on_their_page(
        self, url_name: str, model: type[Positie] | type[PositieType]
    ) -> None:
        first = self.page(url_name, 1)
        model.objects.filter(uuid=first[0]).update(omschrijving="bijgewerkt")

        self.assertCountEqual(first + self.page(url_name, 2), uuids(model))

    def test_positie_list(self) -> None:
        PositieFactory.create_batch(2)
        self.assert_edit_keeps_rows_on_their_page("positie", Positie)

    def test_positietype_list(self) -> None:
        PositieTypeFactory.create_batch(2)
        self.assert_edit_keeps_rows_on_their_page("positietype", PositieType)
