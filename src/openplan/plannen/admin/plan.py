from django.contrib import admin

from ..models.plan import Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "naam",
        "status",
        "startdatum",
    )

    list_filter = ("status",)

    search_fields = (
        "uuid",
        "naam",
    )

    readonly_fields = ("uuid", "gewijzigd_op")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "naam",
                    "omschrijving",
                    "status",
                    "tsaverwijzing",
                    "zaak",
                    "contactmoment",
                    "eigenaar",
                ),
            },
        ),
        (
            "Data",
            {
                "fields": (
                    "startdatum",
                    "einddatum",
                    "beoogde_startdatum",
                    "beoogde_einddatum",
                    "gewijzigd_op",
                ),
            },
        ),
        (
            "Wijziging",
            {
                "fields": (
                    "reden_wijziging",
                    "toelichting_reden",
                ),
            },
        ),
    )
