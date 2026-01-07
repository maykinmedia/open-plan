import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.utils.version_model import VersionedModel


class Plan(VersionedModel):
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4) voor deze functie."),
    )
    plantype = models.ForeignKey(
        "plannen.Plantype",
        on_delete=models.PROTECT,
        help_text=_("Type van het plan."),
    )
    # TODO:
    # Zaak hoort bij plan
    # Link to medewerker in Open Organisatie
    # Link to sociaal domein

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Plannen")

    def __str__(self):
        return str(self.plantype)
