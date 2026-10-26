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

    readonly_fields = ("uuid",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "naam",
                    "beschrijving",
                    "reden_wijziging",
                    "voortgang_toelichting",
                    "status",
                ),
            },
        ),
        (
            "Data",
            {
                "fields": (
                    "startdatum",
                    "einddatum",
                ),
            },
        ),
        (
            "URNs",
            {
                "fields": (
                    "zaak",
                    "contactmoment",
                    "eigenaar",
                ),
            },
        ),
    )
