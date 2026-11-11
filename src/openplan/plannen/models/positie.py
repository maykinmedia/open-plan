import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..enums.status import RedenWijziging


class Positie(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    subject = models.ForeignKey(
        "plannen.Subject",
        on_delete=models.CASCADE,
        related_name="posities",
        help_text=_("Het subject waartoe de positie behoort."),
    )
    positietype = models.ForeignKey(
        "plannen.PositieType",
        on_delete=models.PROTECT,
        related_name="postities",
        help_text=_("Het type van de positie."),
    )
    algoritme = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Algoritme van de positie."),
    )
    naam = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Naam van de positie."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van de postitie."),
    )
    gewijzigd_op = models.DateTimeField(
        auto_now=True,
        help_text=_("Datum en tijd waarop de positie voor het laatst is gewijzigd."),
    )
    reden_wijziging = models.CharField(
        max_length=30,
        choices=RedenWijziging.choices,
        default=RedenWijziging.REGISTREREN,
        help_text=_("Reden waarom de positie gewijzigd is."),
    )
    toelichting_reden = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting reden wijziging van de positie."),
    )

    class Meta:
        verbose_name = _("Positie")
        verbose_name_plural = _("Posities")

    def __str__(self):
        return self.naam
