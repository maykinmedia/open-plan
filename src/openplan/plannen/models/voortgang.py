# openplan/plannen/models/voortgang.py
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Voortgang(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    naam = models.CharField(
        max_length=255,
        help_text=_("Naam van de voortgang."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van de voortgang."),
    )

    class Meta:
        verbose_name = _("Voortgang")
        verbose_name_plural = _("Voortgangen")

    def __str__(self):
        return self.naam
