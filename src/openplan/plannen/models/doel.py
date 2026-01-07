import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.utils.version_model import VersionedModel

from .validators import validate_hoofd_doel_not_self, validate_primary_persoon


class Doel(VersionedModel):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4) voor deze functie."),
    )
    plan = models.ForeignKey(
        "plannen.Plan",
        on_delete=models.CASCADE,
        related_name="doelen",
        help_text=_("Het plan waarbij dit doel hoort."),
    )
    persoon = models.ForeignKey(
        "plannen.Persoon",
        on_delete=models.CASCADE,
        related_name="doelen",
        help_text=_("Het primaire persoon bij wie dit doel hoort."),
    )
    doeltype = models.ForeignKey(
        "plannen.Doeltype",
        on_delete=models.PROTECT,
        related_name="doelen",
        help_text=_("Type van het doel"),
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

    def __str__(self):
        return str(self.plan)

    def clean(self):
        if not self.persoon_id:
            return

        validate_hoofd_doel_not_self(self)
        validate_primary_persoon(self.persoon)
