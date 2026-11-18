import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..enums.status import RedenWijziging
from .validators import nummer_validatie, validate_immutable_field


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
    algoritme = models.CharField(
        max_length=20,
        blank=True,
        validators=[nummer_validatie],
        help_text=_("Algoritme van de positie."),
    )
    naam = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Naam van de positie."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van de postitie."),
    )
    gewijzigd_op = models.DateTimeField(
        auto_now=True,
        help_text=_("Datum en tijd waarop de positie voor het laatst is gewijzigd."),
    )
    reden_wijziging = models.CharField(
        max_length=30,
        choices=RedenWijziging.choices,
        default=RedenWijziging.REGISTREREN,
        help_text=_("Reden waarom de positie gewijzigd is."),
    )
    toelichting_reden = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting reden wijziging van de positie."),
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
        return self.naam

    def clean(self):
        super().clean()
        if not self.positietype_id:
            return

        validate_immutable_field(
            self, "domein", _("Het domein van een positie kan niet veranderen.")
        )
        self._controleer_domein()
        self._controleer_een_positie_per_domein()

    def _controleer_domein(self):
        domein_id = self.positietype.configuraties.values_list(
            "domein_id", flat=True
        ).first()

        if domein_id is None:
            return

        if domein_id != self.domein_id:
            raise ValidationError(
                {
                    "domein": _(
                        "Het domein van de positie moet gelijk zijn aan het domein "
                        "van de configuratie van het positietype."
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
