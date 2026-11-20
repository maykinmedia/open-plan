from typing import Any

from django.db import models

from openplan.plannen.enums.status import RedenWijziging

from .models import WIJZIGING_VELDEN, WijzigingHistoryModel

_REDEN = "_reden_wijziging"
_TOELICHTING = "_toelichting_reden"


def zet_wijziging(instance, reden: str, toelichting: str = "") -> None:
    """
    Attach a reason to the next save of instance. Its history row gets it.

        zet_wijziging(doel, RedenWijziging.CORRIGEREN, "Typfout")
        doel.save()
    """
    setattr(instance, _REDEN, reden)
    setattr(instance, _TOELICHTING, toelichting or "")


def zet_reden_wijziging(sender, instance, history_instance, **kwargs) -> None:
    """
    Receiver for simple_history's pre_create_historical_record.
    Connected in PlannenConfig.ready().
    """
    if not isinstance(history_instance, WijzigingHistoryModel):
        return

    # pop: the reason belongs to this one save, not to later saves.
    reden = instance.__dict__.pop(_REDEN, "")
    toelichting = instance.__dict__.pop(_TOELICHTING, "")

    # No reason given: a default based on the kind of change.
    if not reden:
        if history_instance.history_type == "+":
            reden = RedenWijziging.REGISTREREN
        elif history_instance.history_type == "-":
            reden = RedenWijziging.VERNIETIGEN

    history_instance.reden_wijziging = reden
    history_instance.toelichting_reden = toelichting


def wis_historie_na_verwijderen(
    sender: type[models.Model],
    instance: models.Model,
    history_instance: models.Model,
    **kwargs: Any,
) -> None:
    """
    Receiver for simple_history's post_create_historical_record.
    Connected in PlannenConfig.ready().

    When an object is deleted, remove all of its earlier history and keep
    only the "-" version, with its data emptied. Kept on that row: the
    object's id (needed for 410 Gone), the history_* columns (version id,
    date, type, user) and the reason fields (vernietigen by default).
    """
    if not isinstance(history_instance, WijzigingHistoryModel):
        return
    if history_instance.history_type != "-":
        return

    history_model = type(history_instance)
    pk_naam = instance._meta.pk.name  # "uuid" for Doel
    historie = history_model._default_manager.filter(**{pk_naam: instance.pk})

    # Remove all earlier versions; only this "-" version remains.
    historie.exclude(history_id=history_instance.history_id).delete()

    # Set all data of the remaining version to NULL.
    behouden = {pk_naam, *WIJZIGING_VELDEN}
    leeg = {
        field.attname: None
        for field in history_model._meta.concrete_fields
        if field.name not in behouden and not field.name.startswith("history_")
    }
    historie.update(**leeg)
