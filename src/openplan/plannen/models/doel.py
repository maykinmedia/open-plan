import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.plannen.enums.status import RedenWijziging, Resultaat, Status


class Doel(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    positie = models.ForeignKey(
        "plannen.Positie",
        on_delete=models.CASCADE,
        related_name="doelen",
        help_text=_("De positie waartoe dit doel behoort."),
    )
    # doeltype = models.ForeignKey(
    #     "plannen.Doeltype",
    #     on_delete=models.PROTECT,
    #     related_name="doelen",
    #     help_text=_("Type van het doel"),
    # )
    naam = models.CharField(
        max_length=255,
        help_text=_("Naam van het doel."),
    )
    omschrijving = models.TextField(
        blank=True,
        help_text=_("omschrijving van het doel."),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIEF,
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
        max_length=30,
        choices=RedenWijziging.choices,
        default=RedenWijziging.REGISTREREN,
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
        return self.naam
