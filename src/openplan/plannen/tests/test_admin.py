import json

from django.urls import reverse, reverse_lazy
from django.utils import timezone

from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa

from openplan.accounts.tests.factories import UserFactory

from ..models.factories.doel import DoelFactory
from ..models.subdoel import SubDoel

URN_1 = "urn:nld:gemeenteutrecht:product:uuid:2f463a72-83fd-48bc-a3cf-901755c1644c"
URN_2 = "urn:nld:gemeenteutrecht:product:uuid:8a1b2c3d-1234-4abc-9def-0123456789ab"


@disable_admin_mfa()
class SubDoelAdminTests(WebTest):
    url = reverse_lazy("admin:plannen_subdoel_add")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = UserFactory.create(superuser=True)
        cls.doel = DoelFactory.create()

    def setUp(self) -> None:
        super().setUp()
        self.app.set_user(self.user)

    def _fill_required_fields(self, form):
        form["naam"] = "Test subdoel"
        form["doel"] = self.doel.pk
        form["startdatum"] = timezone.now().date()
        form["beoogde_startdatum"] = timezone.now().date()

    def _create_subdoel(self, producten):
        return SubDoel.objects.create(
            doel=self.doel,
            naam="Bestaand subdoel",
            startdatum=timezone.now().date(),
            beoogde_startdatum=timezone.now().date(),
            producten=producten,
        )

    def _producten_errors(self, response):
        return response.html.find_all(
            "ul", {"class": "errorlist", "id": "id_producten_error"}
        )

    def test_create_subdoel_with_one_product(self):
        self.assertEqual(SubDoel.objects.count(), 0)
        response = self.app.get(self.url)
        form = response.forms.get("subdoel_form")
        self._fill_required_fields(form)

        form["producten"] = json.dumps([{"urn": URN_1}])
        response = form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(SubDoel.objects.count(), 1)
        self.assertEqual(SubDoel.objects.get().producten, [{"urn": URN_1}])

    def test_create_subdoel_with_multiple_products(self):
        response = self.app.get(self.url)
        form = response.forms.get("subdoel_form")
        self._fill_required_fields(form)

        form["producten"] = json.dumps([{"urn": URN_1}, {"urn": URN_2}])
        response = form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            SubDoel.objects.get().producten,
            [{"urn": URN_1}, {"urn": URN_2}],
        )

    def test_create_subdoel_without_products(self):
        response = self.app.get(self.url)
        form = response.forms.get("subdoel_form")
        self._fill_required_fields(form)

        form["producten"] = json.dumps([])
        response = form.submit()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(SubDoel.objects.get().producten, [])

    def test_create_subdoel_invalid_urn(self):
        response = self.app.get(self.url)
        form = response.forms.get("subdoel_form")
        self._fill_required_fields(form)

        form["producten"] = json.dumps([{"urn": URN_1}, {"urn": "geen-geldige-urn"}])
        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SubDoel.objects.count(), 0)

        errors = self._producten_errors(response)
        self.assertEqual(len(errors), 1)
        self.assertIn("geen-geldige-urn", errors[0].get_text(strip=True))
        self.assertIn("does not match", errors[0].get_text(strip=True))

    def test_create_subdoel_invalid_property(self):
        response = self.app.get(self.url)
        form = response.forms.get("subdoel_form")
        self._fill_required_fields(form)

        form["producten"] = json.dumps([{"test": ""}])
        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SubDoel.objects.count(), 0)

        errors = self._producten_errors(response)
        self.assertEqual(len(errors), 1)
        self.assertIn(
            "Additional properties are not allowed ('test' was unexpected)",
            errors[0].get_text(strip=True),
        )

    def test_create_subdoel_duplicate_urns(self):
        response = self.app.get(self.url)
        form = response.forms.get("subdoel_form")
        self._fill_required_fields(form)

        form["producten"] = json.dumps([{"urn": URN_1}, {"urn": URN_1}])
        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SubDoel.objects.count(), 0)

        errors = self._producten_errors(response)
        self.assertEqual(len(errors), 1)
        self.assertIn("non-unique elements", errors[0].get_text(strip=True))

    def test_create_subdoel_invalid_json(self):
        response = self.app.get(self.url)
        form = response.forms.get("subdoel_form")
        self._fill_required_fields(form)

        form["producten"] = f'[{{"urn": "{URN_1}"}},]'
        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SubDoel.objects.count(), 0)
        self.assertEqual(len(self._producten_errors(response)), 1)

    def test_change_subdoel_remove_product(self):
        subdoel = self._create_subdoel([{"urn": URN_1}, {"urn": URN_2}])
        url = reverse("admin:plannen_subdoel_change", args=[subdoel.pk])

        response = self.app.get(url)
        form = response.forms.get("subdoel_form")
        form["producten"] = json.dumps([{"urn": URN_2}])
        response = form.submit()

        self.assertEqual(response.status_code, 302)
        subdoel.refresh_from_db()
        self.assertEqual(subdoel.producten, [{"urn": URN_2}])
