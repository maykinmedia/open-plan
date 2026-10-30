import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..enums.status import Status


class SubdoelType(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    configuraties = models.ManyToManyField(
        "plannen.Configuratie",
        blank=True,
        related_name="subdoeltypen",
        help_text=_("Configuraties gekoppeld aan dit subdoeltype."),
    )
    naam = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Naam van het subdoeltype."),
    )
    omschrijving = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Omschrijving van het subdoeltype."),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIEF,
        help_text=_("Status van het subdoeltype."),
    )
    gewenst_resultaat = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Gewenst resultaat van het subdoeltype."),
    )
    toelichting_inwoner = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting inwoner van het subdoeltype."),
    )
    toelichting_medewerker = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting medewerker van het subdoeltype."),
    )

    class Meta:
        verbose_name = _("Subdoeltype")
        verbose_name_plural = _("Subdoeltypen")

    def __str__(self):
        return self.naam
