import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from vng_api_common.fields import BSNField

from openplan.utils.fields import URNField

from ..enums.status import Status, Type


class Subject(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    plan = models.ForeignKey(
        "plannen.Plan",
        on_delete=models.CASCADE,
        related_name="subjecten",
        help_text=_("Het plan waartoe dit subject behoort."),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIEF,
        help_text=_("Status van het subject."),
    )
    rolbeschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Rolbeschrijving van het subject."),
    )
    type = models.CharField(
        choices=Type.choices,
        blank=True,
        help_text=_("Het type subject"),
    )
    profiel = URNField(
        blank=True,
        help_text=_("URN naar het profiel."),
    )
    klant = URNField(
        blank=True,
        help_text=_("URN naar de Klant "),
    )
    bsn = BSNField(
        blank=True,
        help_text=_("BSN voor BRP-koppeling "),
    )

    class Meta:
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjecten")

    def __str__(self):
        return f"Subject {self.uuid}"
