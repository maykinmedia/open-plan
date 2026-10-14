import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.plannen.enums.status import PlanStatus, Resultaat


class SubDoel(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    doel = models.ForeignKey(
        "plannen.Doel",
        on_delete=models.CASCADE,
        related_name="doelen",
        help_text=_("Het doel waartoe dit subdoel behoort."),
    )
    titel = models.CharField(
        max_length=255,
        help_text=_("Titel van het subdoel."),
    )
    beschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Beschrijving van het subdoel."),
    )
    status = models.CharField(
        max_length=20,
        choices=PlanStatus.choices,
        default=PlanStatus.ACTIEF,
        help_text=_("Status van het subdoel."),
    )
    startdatum = models.DateTimeField(
        help_text=_("Startdatum van het subdoel."),
        db_index=True,
    )
    einddatum = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Einddatum van het subdoel."),
    )
    resultaat = models.CharField(
        max_length=20,
        choices=Resultaat.choices,
        blank=True,
        help_text=_("Resultaat van het subdoel."),
    )
    reden_wijziging = models.CharField(
        max_length=20,
        choices=Resultaat.choices,
        blank=True,
        help_text=_("Reden waarom het gewijzigd is."),
    )
    voortgang_toelichting = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting bij de voortgang van het subdoel."),
    )

    class Meta:
        verbose_name = _("Subdoel")
        verbose_name_plural = _("Subdoelen")
        ordering = ("-startdatum",)

    def __str__(self):
        return self.titel
