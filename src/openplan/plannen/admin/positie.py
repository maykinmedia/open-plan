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
    readonly_fields = ("uuid", "gewijzigd_op")

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
                    "gewijzigd_op",
                    "reden_wijziging",
                    "toelichting_reden",
                ),
            },
        ),
    )
