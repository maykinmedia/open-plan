import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..enums.status import Status


class EvaluatieType(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    naam = models.CharField(
        max_length=255,
        help_text=_("Naam van het evaluatie type."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van het evaluatie type."),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIEF,
        help_text=_("Status van het evaluatie type."),
    )
    toelichting_inwoner = models.TextField(
        blank=True,
        help_text=_("Toelichting inwoner van het evaluatietype."),
    )
    toelichting_medewerker = models.TextField(
        blank=True,
        help_text=_("Toelichting medewerker van het evaluatietype."),
    )

    class Meta:
        verbose_name = _("Evaluatietype")
        verbose_name_plural = _("Evaluatietypen")

    def __str__(self):
        return self.naam
