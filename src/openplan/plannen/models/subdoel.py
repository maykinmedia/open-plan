import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.plannen.enums.status import Doelstatus, RedenWijziging

from .validators import validate_dates, validate_immutable_field


class Subdoel(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    doel = models.ForeignKey(
        "plannen.Doel",
        on_delete=models.CASCADE,
        related_name="subdoelen",
        help_text=_("Het doel waartoe dit subdoel behoort."),
    )
    subdoeltype = models.ForeignKey(
        "plannen.Subdoeltype",
        on_delete=models.PROTECT,
        related_name="subdoelen",
        help_text=_("Type van het subdoel"),
    )
    naam = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Naam van het subdoel."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van het subdoel."),
    )
    status = models.CharField(
        max_length=20,
        choices=Doelstatus.choices,
        default=Doelstatus.GEPLAND,
        help_text=_("Status van het subdoel."),
    )
    startdatum = models.DateField(
        help_text=_("Startdatum van het subdoel."),
        db_index=True,
    )
    einddatum = models.DateField(
        null=True,
        blank=True,
        help_text=_("Einddatum van het subdoel."),
    )
    beoogde_startdatum = models.DateField(
        help_text=_("Beoogde startdatum van het subdoel."),
        db_index=True,
    )
    beoogde_einddatum = models.DateField(
        null=True,
        blank=True,
        help_text=_("Beoogde einddatum van het subdoel."),
    )
    gewijzigd_op = models.DateTimeField(
        auto_now=True,
        help_text=_("Datum en tijd waarop het subdoel voor het laatst is gewijzigd."),
    )
    notitie_intern = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Notitie intern."),
    )
    notitie_extern = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Notitie extern."),
    )
    voortgang = models.ForeignKey(
        "plannen.Voortgang",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subdoelen",
        help_text=_("Voortgang van het subdoel."),
    )
    reden_wijziging = models.CharField(
        max_length=30,
        choices=RedenWijziging.choices,
        default=RedenWijziging.REGISTREREN,
        help_text=_("Reden waarom het gewijzigd is."),
    )
    toelichting_reden = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting reden wijziging van het subdoel."),
    )

    class Meta:
        verbose_name = _("Subdoel")
        verbose_name_plural = _("Subdoelen")
        ordering = ("-startdatum",)

    def __str__(self):
        return self.naam

    def clean(self):
        super().clean()
        validate_dates(self.startdatum, self.einddatum)
        validate_dates(self.beoogde_startdatum, self.beoogde_einddatum)

        validate_immutable_field(
            self,
            "subdoeltype",
            _("Het subdoeltype kan niet gewijzigd worden. Maak een nieuw subdoel aan."),
        )
