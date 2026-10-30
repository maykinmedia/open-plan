import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..enums.status import RedenWijziging, Status


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
    positietype = models.ForeignKey(
        "plannen.PositieType",
        on_delete=models.PROTECT,
        related_name="posities",
        help_text=_("Het type van de positie."),
    )
    domein = models.ForeignKey(
        "plannen.Domein",
        on_delete=models.PROTECT,
        related_name="+",
        editable=False,
        help_text=_("Het domein van de positie."),
    )
    beschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Beschrijving van de postitie."),
    )
    reden_wijziging = models.CharField(
        max_length=30,
        choices=RedenWijziging.choices,
        default=RedenWijziging.REGISTREREN,
        help_text=_("Reden waarom het gewijzigd is."),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIEF,
        help_text=_("Status van het doel."),
    )
    voortgang_toelichting = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Voortgangstoelichting van de postitie."),
    )

    class Meta:
        verbose_name = _("Positie")
        verbose_name_plural = _("Posities")

        constraints = [
            models.UniqueConstraint(
                fields=["subject", "domein"],
                name="max_een_positie_per_subject_per_domein",
            )
        ]

    def __str__(self):
        return str(self.uuid)

    def _controleer_domein(self):
        domein_id = self.positietype.configuratie.domein_id
        if self._state.adding:
            self.domein_id = domein_id
        elif domein_id != self.domein_id:
            raise ValidationError(
                {
                    "positietype": _(
                        "Het positietype hoort bij een ander domein dan deze positie."
                    )
                }
            )

    def clean(self):
        super().clean()
        if self.positietype_id:
            self._controleer_domein()
            if (
                self._state.adding
                and Positie.objects.filter(
                    subject_id=self.subject_id, domein_id=self.domein_id
                ).exists()
            ):
                raise ValidationError(
                    _("Dit subject heeft al een positie in dit domein.")
                )

    def save(self, *args, **kwargs):
        self._controleer_domein()
        super().save(*args, **kwargs)
