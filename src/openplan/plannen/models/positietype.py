import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..enums.status import Status
from .validators import validate_positie_type_not_self


class PositieType(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    configuraties = models.ManyToManyField(
        "plannen.Configuratie",
        blank=True,
        related_name="positietypen",
        help_text=_("Configuraties gekoppeld aan dit positietypen."),
    )
    naam = models.CharField(
        max_length=255,
        help_text=_("Naam van het positietype."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van het positietype."),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIEF,
        help_text=_("Status van het positietype."),
    )
    startpositie = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Startpositie van het positietype."),
    )
    eindpositie = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Eindpositie van het positietype."),
    )
    doelpositie = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Doelpositie van het positietype."),
    )

    class Meta:
        verbose_name = _("Positietype")
        verbose_name_plural = _("Positietypen")

    def __str__(self):
        return self.naam

    def clean(self):
        super().clean()

        validate_positie_type_not_self(self)
