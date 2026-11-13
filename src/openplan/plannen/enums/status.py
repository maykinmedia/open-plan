from django.db import models
from django.utils.translation import gettext_lazy as _


# TODO: Remove this status
class Status(models.TextChoices):
    ACTIEF = "actief", _("Actief")
    NIET_ACTIEF = "niet_actief", _("Niet actief")


class TypeStatus(models.TextChoices):
    ACTIEF = "actief", _("Actief")
    NIET_ACTIEF = "niet_actief", _("Niet actief")


class DoelStatus(models.TextChoices):
    GEPLAND = "gepland", _("Gepland")
    GESTART = "gestart", _("Gestart")
    BEHAALD = "behaald", _("Behaald")
    AFGEBROKEN = "afgebroken", _("Afgebroken")


class SubjectType(models.TextChoices):
    PERSOON = "persoon", _("Persoon")
    FYSIEK_OBJECT = "fysiek_object", _("Fysiek object")


class Resultaat(models.TextChoices):
    BEHAALD = "behaald", _("Behaald")
    ACTIEF = "actief", _("Actief")
    NIET_BEHAALD = "niet_behaald", _("Niet behaald")


class RedenWijziging(models.TextChoices):
    REGISTREREN = "registreren", _("Registreren")
    WIJZIGEN = "wijzigen", _("Wijzigen")
    CORRIGEREN = "corrigeren", _("Corrigeren")
    HERZIEN = "herzien", _("Herzien")
    ONGEDAANMAKEN = "ongedaan_maken", _("Ongedaan maken")
    VERNIETIGEN = "vernietigen", _("Vernietigen")
    OVERBRENGEDEPOT = "overbrengen_depot", _("Overbrengen depot")
