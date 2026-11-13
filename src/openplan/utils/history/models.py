from django.db import models
from django.utils.translation import gettext_lazy as _

from simple_history.models import HistoricalRecords

from openplan.plannen.enums.status import RedenWijziging


class WijzigingHistoryModel(models.Model):
    """
    Extra columns on every history table (HistoricalDoel, ...).
    Filled in by signals.zet_reden_wijziging.
    """

    reden_wijziging = models.CharField(
        max_length=30,
        choices=RedenWijziging.choices,
        blank=True,
        help_text=_("Reden waarom het gewijzigd is."),
    )
    toelichting_reden = models.TextField(
        blank=True,
        max_length=1000,
        help_text=_("Toelichting op de reden van de wijziging."),
    )

    class Meta:
        abstract = True


class HistorieRecords(HistoricalRecords):
    """
    Use instead of HistoricalRecords:

        history = HistorieRecords()
    """

    def __init__(self, *args, bases=(WijzigingHistoryModel,), **kwargs):
        super().__init__(*args, bases=bases, **kwargs)
