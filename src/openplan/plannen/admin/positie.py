from django.contrib import admin

from ..models.positie import Positie


@admin.register(Positie)
class PositieAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "naam",
        "omschrijving",
    )
    search_fields = ("uuid",)
    readonly_fields = ("uuid",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "subject",
                    "positie_type",
                    "naam",
                    "omschrijving",
                    "status",
                    "reden_wijziging",
                    "toelichting_reden",
                ),
            },
        ),
    )
