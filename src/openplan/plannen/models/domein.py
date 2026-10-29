import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.plannen.enums.status import Status


class Domein(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    naam = models.CharField(
        max_length=255,
        help_text=_("Naam van het domein."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van het domein."),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIEF,
        help_text=_("Status van het domein."),
    )

    class Meta:
        verbose_name = _("Domein")
        verbose_name_plural = _("Domeinen")

    def __str__(self):
        return self.naam
