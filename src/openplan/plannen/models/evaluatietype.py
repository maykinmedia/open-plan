import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..enums.status import PlanStatus


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
    # TODO: fix to right status after #40 is merged
    status = models.CharField(
        max_length=20,
        choices=PlanStatus.choices,
        default=PlanStatus.ACTIEF,
        help_text=_("Status van het evaluatie type."),
    )

    class Meta:
        verbose_name = "Evaluatietype"
        verbose_name_plural = "Evaluatietypen"

    def __str__(self):
        return self.naam
