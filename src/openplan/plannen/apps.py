from django.apps import AppConfig


class PlannenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "openplan.plannen"

    def ready(self):
        from simple_history.signals import (
            post_create_historical_record,
            pre_create_historical_record,
        )

        from openplan.utils.history.signals import (
            wis_historie_na_verwijderen,
            zet_reden_wijziging,
        )

        from . import metrics  # noqa

        pre_create_historical_record.connect(
            zet_reden_wijziging,
            dispatch_uid="history_zet_reden_wijziging",
        )

        post_create_historical_record.connect(
            wis_historie_na_verwijderen,
            dispatch_uid="wis_historie_na_verwijderen",
        )
