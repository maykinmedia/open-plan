import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from openplan.utils.fields import URNField


class Positie(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    subject = models.ForeignKey(
        "plannen.Subject",
        on_delete=models.CASCADE,
        related_name="posities",
        help_text=_("Het subject waartoe de positie behoort."),
    )
    positie_type = models.ForeignKey(
        "plannen.PositieType",
        on_delete=models.PROTECT,
        related_name="postities",
        help_text=_("Het type van de positie."),
    )
    beschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Beschrijving van de postitie."),
    )
    # TODO: categorie stamtabel nog te definieren
    reden_wijziging = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Reden waarom de postitie is gewijzigd."),
    )
    voortgang_toelichting = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Voortgangstoelichting van de postitie."),
    )
    eigenaar = URNField(
        help_text=_("URN naar de eigenaar in het HR-systeem."),
        blank=True,
    )

    class Meta:
        verbose_name = _("Positie")
        verbose_name_plural = _("Posities")

    def __str__(self):
        return str(self.uuid)
