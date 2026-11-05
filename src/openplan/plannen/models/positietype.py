import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..enums.status import Status
from .validators import validate_immutable_field, validate_positie_type_not_self


class PositieType(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    configuraties = models.ManyToManyField(
        "plannen.Configuratie",
        blank=True,
        related_name="positietypen",
        help_text=_("Configuraties gekoppeld aan dit positietypen."),
    )
    domein = models.ForeignKey(
        "plannen.Domein",
        on_delete=models.PROTECT,
        related_name="positietypen",
        help_text=_("Het domein waartoe dit positietype behoort."),
    )
    naam = models.CharField(
        max_length=255,
        help_text=_("Naam van het positietype."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van het positietype."),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIEF,
        help_text=_("Status van het positietype."),
    )
    startpositie = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Startpositie van het positietype."),
    )
    eindpositie = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Eindpositie van het positietype."),
    )
    toelichting_inwoner = models.TextField(
        blank=True,
        help_text=_("Toelichting inwoner van het positietype."),
    )
    toelichting_medewerker = models.TextField(
        blank=True,
        help_text=_("Toelichting medewerker van het positietype."),
    )
    doelpositie = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Doelpositie van het positietype."),
    )

    class Meta:
        verbose_name = _("Positietype")
        verbose_name_plural = _("Positietypen")

    def __str__(self):
        return self.naam

    def clean(self):
        super().clean()

        validate_positie_type_not_self(self)
        self._controleer_domein_ongewijzigd()

    def _controleer_domein_ongewijzigd(self):
        if self._state.adding or not self.posities.exists():
            return
        validate_immutable_field(
            self,
            "domein",
            _(
                "Het domein kan niet gewijzigd worden, dit positietype wordt al gebruikt."
            ),
        )

    def controleer_configuraties(self, configuraties, domein):
        if any(configuratie.domein_id != domein.pk for configuratie in configuraties):
            raise ValidationError(
                {
                    "configuraties": _(
                        "Alle configuraties moeten bij het domein van dit positietype horen."
                    )
                }
            )
