from openplan.plannen.enums.status import RedenWijziging

from .models import WijzigingHistoryModel

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

    # First version of a new object.
    if not reden and history_instance.history_type == "+":
        reden = RedenWijziging.REGISTREREN

    history_instance.reden_wijziging = reden
    history_instance.toelichting_reden = toelichting
