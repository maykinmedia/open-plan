import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.plannen.enums.status import PlanStatus, Resultaat


class Doel(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    # TODO: change to subject
    persoon = models.ForeignKey(
        "plannen.Persoon",
        on_delete=models.CASCADE,
        related_name="doelen",
        help_text=_("Het persoon bij wie dit doel hoort."),
    )
    titel = models.CharField(
        max_length=255,
        help_text=_("Titel van het doel."),
    )
    beschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Beschrijving van het doel."),
    )
    status = models.CharField(
        max_length=20,
        choices=PlanStatus.choices,
        default=PlanStatus.ACTIEF,
        help_text=_("Status van het doel."),
    )
    startdatum = models.DateTimeField(
        help_text=_("Startdatum van het doel."),
        db_index=True,
    )
    einddatum = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Einddatum van het doel."),
    )
    resultaat = models.CharField(
        max_length=20,
        choices=Resultaat.choices,
        blank=True,
        help_text=_("Resultaat van het doel."),
    )
    reden_wijziging = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Reden waarom het gewijzigd is."),
    )
    voortgang_toelichting = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting bij de voortgang van het doel."),
    )

    class Meta:
        verbose_name = _("Doel")
        verbose_name_plural = _("Doelen")
        ordering = ("-startdatum",)

    def __str__(self):
        return self.titel
