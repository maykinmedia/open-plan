from django.apps import AppConfig

import pghistory


class PlannenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "openplan.plannen"

    def ready(self):
        from .models import Doel, Plan

        for model in (Plan, Doel):
            pghistory.track(
                model,
                context_field="version_context",
            )
