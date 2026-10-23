import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.plannen.enums.status import Status
from openplan.utils.fields import URNField


class Contactmoment(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    plan = models.ForeignKey(
        "plannen.Plan",
        on_delete=models.CASCADE,
        related_name="contactmomenten",
        help_text=_("Het plan waarbij dit contactmoment hoort."),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIEF,
        help_text=_("Status van het contactmoment."),
    )
    toelichting_status = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting bij de status van het contactmoment."),
    )
    datum = models.DateTimeField(
        help_text=_("Startdatum van het contactmoment."),
        db_index=True,
    )
    notitie = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Notitie bij het contactmoment."),
    )

    persoonsprofiel = URNField(
        blank=True,
        help_text=_(
            "URL naar het persoonsprofiel (alleen voor primaire personen verplicht)."
        ),
    )

    class Meta:
        verbose_name = _("Contactmoment")
        verbose_name_plural = _("Contactmomenten")
        ordering = ("-datum",)

    def __str__(self):
        return str(self.uuid)
