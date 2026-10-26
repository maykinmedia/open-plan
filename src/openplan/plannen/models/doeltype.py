import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..enums.doel import DoelTypeEnum


class DoelType(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        help_text=_("Unieke resource identifier (UUID4)."),
    )
    doel_type = models.CharField(
        max_length=50,
        choices=DoelTypeEnum.choices,
        help_text=_("Het type doel."),
    )

    class Meta:
        verbose_name = "Doeltype"
        verbose_name_plural = "Doeltypen"

    def __str__(self):
        return self.doel_type
