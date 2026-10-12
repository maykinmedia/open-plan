import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.plannen.enums.status import DoelStatus
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
    evaluatietype = models.ForeignKey(
        "plannen.Evaluatietype",
        on_delete=models.PROTECT,
        related_name="evaluaties",
        help_text=_("Het type evaluatie."),
    )
    posities = models.ManyToManyField(
        "plannen.Positie",
        related_name="evaluaties",
        blank=True,
        help_text=_("De posities die bij deze evaluatie horen."),
    )
    doelen = models.ManyToManyField(
        "plannen.Doel",
        related_name="evaluaties",
        blank=True,
        help_text=_("De doelen die bij deze evaluatie horen."),
    )
    subdoelen = models.ManyToManyField(
        "plannen.Subdoel",
        related_name="evaluaties",
        blank=True,
        help_text=_("De subdoelen die bij deze evaluatie horen."),
    )
    naam = models.CharField(
        max_length=255,
        help_text=_("Naam van de evaluatie."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van de evaluatie."),
    )
    status = models.CharField(
        max_length=20,
        choices=DoelStatus.choices,
        default=DoelStatus.GEPLAND,
        help_text=_("Status van de evaluatie."),
    )
    datum = models.DateTimeField(
        help_text=_("Datum van de evaluatie."),
        db_index=True,
    )
    contactmoment = URNField(
        blank=True,
        help_text=_("URL naar het contactmoment."),
    )
    eigenaar = URNField(
        blank=True,
        help_text=_("URL naar de eigenaar."),
    )
    zaak = URNField(
        help_text=_("URN naar de bijbehorende zaak in het zaaksysteem."),
        blank=True,
    )
    verslag = URNField(
        help_text=_("URN naar een bijbehorende document in een DRC."),
        blank=True,
    )

    class Meta:
        verbose_name = _("Evaluatie")
        verbose_name_plural = _("Evaluaties")
        ordering = ("-datum",)

    def __str__(self):
        return str(self.uuid)
