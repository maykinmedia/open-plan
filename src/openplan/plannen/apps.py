from django.apps import AppConfig


class PlannenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "openplan.plannen"

    def ready(self):
        from simple_history.signals import pre_create_historical_record

        from openplan.utils.history.signals import zet_reden_wijziging

        from . import metrics  # noqa

        pre_create_historical_record.connect(
            zet_reden_wijziging,
            dispatch_uid="history_zet_reden_wijziging",
        )
