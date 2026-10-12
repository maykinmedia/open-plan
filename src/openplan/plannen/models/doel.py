import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.plannen.enums.status import PlanStatus, Resultaat

from .validators import validate_hoofd_doel_not_self


class Doel(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    plannen = models.ManyToManyField(
        "plannen.Plan",
        related_name="doelen",
        help_text=_("Plannen waaraan dit doel gekoppelt is."),
    )
    persoon = models.ForeignKey(
        "plannen.Subject",
        on_delete=models.CASCADE,
        related_name="doelen",
        help_text=_("Het primaire subject bij wie dit doel hoort."),
    )
    doeltype = models.ForeignKey(
        "plannen.Doeltype",
        on_delete=models.PROTECT,
        related_name="doelen",
        help_text=_("Type van het doel"),
    )
    status = models.CharField(
        max_length=20,
        choices=PlanStatus.choices,
        default=PlanStatus.ACTIEF,
        help_text=_("Status van het doel."),
    )
    titel = models.CharField(
        max_length=255,
        help_text=_("Titel van het doel."),
    )
    beschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Beschrijving van het doel."),
    )
    startdatum = models.DateTimeField(
        help_text=_("Startdatum van het doel."),
        db_index=True,
    )
    einddatum = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Einddatum van het doel."),
    )
    resultaat = models.CharField(
        max_length=20,
        choices=Resultaat.choices,
        blank=True,
        help_text=_("Resultaat van het doel."),
    )
    toelichting_resultaat = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting bij het resultaat van het doel."),
    )

    hoofd_doel = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="subdoelen",
        help_text=_("Optionele koppeling naar een bovenliggend doel."),
    )

    class Meta:
        verbose_name = _("Doel")
        verbose_name_plural = _("Doelen")
        ordering = ("-startdatum",)

    def __str__(self):
        return self.titel

    def clean(self):
        super().clean()

        if not self.persoon:
            return

        validate_hoofd_doel_not_self(self)
