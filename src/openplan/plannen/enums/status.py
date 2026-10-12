from django.db import models
from django.utils.translation import gettext_lazy as _


class PlanStatus(models.TextChoices):
    NIEUW = "nieuw", _("Nieuw")
    ACTIEF = "actief", _("Actief")
    AFGEROND = "afgerond", _("Afgerond")
    AFGEBROKEN = "afgebroken", _("Afgebroken")
    PAUZE = "pauze", _("Pauze")


class SubjectStatus(models.TextChoices):
    NIEUW = "nieuw", _("Nieuw")
    INACTIEF = "inactief", _("Inactief")


class Resultaat(models.TextChoices):
    BEHAALD = "behaald", _("Behaald")
    GEFAALD = "gefaald", _("Gefaald")
