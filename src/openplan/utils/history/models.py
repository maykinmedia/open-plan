import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from simple_history.models import HistoricalRecords

from openplan.plannen.enums.status import RedenWijziging

WIJZIGING_VELDEN = ("reden_wijziging", "toelichting_reden")


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
        kwargs.setdefault(
            "history_id_field",
            models.UUIDField(default=uuid.uuid4, editable=False),
        )
        super().__init__(*args, bases=bases, **kwargs)

    def copy_fields(self, model):
        """
        Make every field copied from the model nullable in the history table.
        The model itself is unchanged: its fields stay required there.
        """
        fields = super().copy_fields(model)
        for field in fields.values():
            field.null = True
        return fields
