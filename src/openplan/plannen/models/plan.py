import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.utils.fields import URNField

from ..enums.status import PlanStatus


class Plan(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    naam = models.CharField(
        max_length=255,
        help_text=_("Naam van het plan."),
    )
    beschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Beschrijving van het plan."),
    )
    status = models.CharField(
        max_length=20,
        choices=PlanStatus.choices,
        default=PlanStatus.NIEUW,
        help_text=_("Status van het plan."),
    )
    fase = models.CharField(
        max_length=20,
        choices=PlanStatus.choices,
        default=PlanStatus.ACTIEF,
        help_text=_("Fase van het plan."),
    )
    startdatum = models.DateTimeField(
        help_text=_("Startdatum van het plan."),
        db_index=True,
    )
    einddatum = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Einddatum van het plan."),
    )
    reden_wijziging = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Reden waarom het plan is gewijzigd."),
    )
    voortgang_toelichting = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting op de voortgang van het plan."),
    )
    # TODO:
    # Multiple uri's???
    zaak = URNField(
        help_text=_("URN naar de bijbehorende zaak in het zaaksysteem."),
        blank=True,
    )
    contactmoment = URNField(
        help_text=_("URN naar het contactmoment in Open Klant."),
        blank=True,
    )
    eigenaar = URNField(
        help_text=_("URN naar de eigenaar in het HR-systeem."),
        blank=True,
    )

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Plannen")
        ordering = ("-startdatum",)

    def __str__(self):
        return str(self.plantype)
