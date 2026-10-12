import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.plannen.enums.status import PlanStatus
from openplan.utils.fields import URNField


class Evaluatie(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    plan = models.ForeignKey(
        "plannen.Plan",
        on_delete=models.CASCADE,
        related_name="evaluaties",
        help_text=_("Het plan waarbij deze evaluatie hoort."),
    )
    evaluatie_type = models.ForeignKey(
        "plannen.EvaluatieType",
        on_delete=models.PROTECT,
        related_name="evaluaties",
        help_text=_("Het type evaluatie."),
    )
    status = models.CharField(
        max_length=20,
        choices=PlanStatus.choices,
        default=PlanStatus.ACTIEF,
        help_text=_("Status van de evaluatie."),
    )
    toelichting_status = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting bij de status van de evaluatie."),
    )
    datum = models.DateTimeField(
        help_text=_("Datum van de evaluatie."),
        db_index=True,
    )
    notitie = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Notitie bij de evaluatie."),
    )

    contactmoment = URNField(
        blank=True,
        help_text=_("URL naar de contactmoment."),
    )
    eigenaar = URNField(
        blank=True,
        help_text=_("URL naar de eigenaar."),
    )
    zaak = URNField(
        help_text=_("URN naar de bijbehorende zaak in het zaaksysteem."),
        blank=True,
    )
    document = URNField(
        help_text=_("URN naar een bijbehorende document in een DRC."),
        blank=True,
    )

    class Meta:
        verbose_name = _("Evaluatie")
        verbose_name_plural = _("Evaluaties")
        ordering = ("-datum",)

    def __str__(self):
        return str(self.uuid)
