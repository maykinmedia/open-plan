import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.utils.fields import URNField

from ..enums.status import Planstatus
from .validators import validate_dates


class Plan(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    naam = models.CharField(
        max_length=255,
        help_text=_("Naam van het plan."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van het plan."),
    )
    status = models.CharField(
        max_length=20,
        choices=Planstatus.choices,
        default=Planstatus.CONCEPT,
        help_text=_("Status van het plan."),
    )
    startdatum = models.DateField(
        help_text=_("Startdatum van het plan."),
        db_index=True,
    )
    einddatum = models.DateField(
        null=True,
        blank=True,
        help_text=_("Einddatum van het plan."),
    )
    beoogde_startdatum = models.DateField(
        help_text=_("Beoogde startdatum van het plan."),
        db_index=True,
    )
    beoogde_einddatum = models.DateField(
        null=True,
        blank=True,
        help_text=_("Beoogde einddatum van het plan."),
    )
    gewijzigd_op = models.DateTimeField(
        auto_now=True,
        help_text=_("Datum en tijd waarop het plan voor het laatst is gewijzigd."),
    )
    reden_wijziging = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Reden waarom het plan is gewijzigd."),
    )
    toelichting_reden = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting reden wijziging van het plan."),
    )
    tsaverwijzing = URNField(
        help_text=_(
            "URN-verwijzing naar het dossier van de ZAAK in een taak specifieke applicatie (TSA)."
        ),
        blank=True,
    )
    # TODO:
    # Multiple uri's???
    zaak = URNField(
        help_text=_("URN naar de bijbehorende zaak in het zaaksysteem."),
        blank=True,
    )
    contactmoment = URNField(
        help_text=_("URN naar het contactmoment in Open Klant."),
        blank=True,
    )
    eigenaar = URNField(
        help_text=_("URN naar de eigenaar in het HR-systeem."),
        blank=True,
    )

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Plannen")
        ordering = ("-startdatum",)

    def __str__(self):
        return self.naam

    def clean(self):
        super().clean()
        validate_dates(self.startdatum, self.einddatum)
        validate_dates(self.beoogde_startdatum, self.beoogde_einddatum)
