import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.plannen.enums.status import Status
from openplan.utils.fields import URNField


class Configuratie(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    domein = models.ForeignKey(
        "plannen.Domein",
        on_delete=models.CASCADE,
        related_name="configuraties",
        help_text=_("De domein waar deze configuratie toe behoort."),
    )
    naam = models.CharField(
        max_length=255,
        help_text=_("Naam van de configuratie."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van de configuratie."),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIEF,
        help_text=_("Status van de configuratie."),
    )
    eigenaar = URNField(
        help_text=_("URN naar de eigenaar van de configuratie."),
        blank=True,
    )

    class Meta:
        verbose_name = _("Configuratie")
        verbose_name_plural = _("Configuraties")

    def __str__(self):
        return str(self.naam)
