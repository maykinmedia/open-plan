import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..enums.status import PlanStatus


class DoelType(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
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
        choices=PlanStatus.choices,
        default=PlanStatus.NIEUW,
        help_text=_("Status van het positietype."),
    )
    gewenst_resultaat = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Startpositie van het positietype."),
    )

    class Meta:
        verbose_name = _("Doeltype")
        verbose_name_plural = _("Doeltypen")

    def __str__(self):
        return str(self.naam)
