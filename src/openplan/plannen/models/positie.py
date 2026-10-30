import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..enums.status import RedenWijziging, Status
from .validators import validate_immutable_field


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
        help_text=_("Het domein van de positie."),
    )
    naam = models.CharField(
        max_length=255,
        help_text=_("Naam van de positie."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van de postitie."),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIEF,
        help_text=_("Status van het doel."),
    )
    reden_wijziging = models.CharField(
        max_length=30,
        choices=RedenWijziging.choices,
        default=RedenWijziging.REGISTREREN,
        help_text=_("Reden waarom het gewijzigd is."),
    )
    toelichting_reden = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting reden wijziging van het subdoel."),
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

    def clean(self):
        super().clean()
        if not self.positietype_id:
            return

        validate_immutable_field(
            self, "domein", _("Het domein van een positie kan niet veranderen.")
        )
        self._controleer_domein()
        self._controleer_een_positie_per_domein()

    def _bepaal_domein_id(self):
        domein_id = self.positietype.configuraties.values_list(
            "domein_id", flat=True
        ).first()
        if domein_id is None:
            raise ValidationError(
                {"positietype": _("Dit positietype heeft geen configuratie.")}
            )
        return domein_id

    def _controleer_domein(self):
        domein_id = self._bepaal_domein_id()
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

    def _controleer_een_positie_per_domein(self):
        if (
            Positie.objects.filter(subject_id=self.subject_id, domein_id=self.domein_id)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                {"subject": _("Dit subject heeft al een positie in dit domein.")}
            )
