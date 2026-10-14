from django.db import models
from django.utils.translation import gettext_lazy as _


class InstrumentTypeEnum(models.TextChoices):
    # voorbeelden
    TRAINING = (
        "training",
        _("Training"),
    )
    COACHING = (
        "coaching",
        _("Coaching"),
    )
    FINANCIËLE_STEUNING = (
        "financiele_ondersteuning",
        _("Financiele ondersteuning"),
    )
