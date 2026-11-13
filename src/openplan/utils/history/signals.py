from openplan.plannen.enums.status import RedenWijziging

from .models import WijzigingHistoryModel


def zet_reden_wijziging(sender, instance, history_instance, **kwargs):
    """
    Runs just before simple-history inserts a history row.

    Takes the reason from the object being saved:
        doel._reden_wijziging = "..."
        doel._toelichting_reden = "..."
        doel.save()
    """
    if not isinstance(history_instance, WijzigingHistoryModel):
        return

    # pop: the reason belongs to this one save, not to later saves.
    reden = instance.__dict__.pop("_reden_wijziging", "")
    toelichting = instance.__dict__.pop("_toelichting_reden", "")

    if not reden and history_instance.history_type == "+":
        reden = RedenWijziging.REGISTREREN

    history_instance.reden_wijziging = reden or ""
    history_instance.toelichting_reden = toelichting or ""
