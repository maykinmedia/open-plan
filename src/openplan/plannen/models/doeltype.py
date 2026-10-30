import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..enums.status import Status


class DoelType(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    configuraties = models.ManyToManyField(
        "plannen.Configuratie",
        blank=True,
        related_name="doeltypen",
        help_text=_("Configuraties gekoppeld aan dit doeltype."),
    )
    naam = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Naam van het doeltype."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van het doeltype."),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIEF,
        help_text=_("Status van het doeltype."),
    )
    gewenst_resultaat = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Gewenst resultaat van het doeltype."),
    )
    toelichting_inwoner = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting inwoner van het doeltype."),
    )
    toelichting_medewerker = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting medewerker van het doeltype."),
    )

    class Meta:
        verbose_name = _("Doeltype")
        verbose_name_plural = _("Doeltypen")

    def __str__(self):
        return self.naam
