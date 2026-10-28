from django.contrib import admin

from ..models.positietype import PositieType


@admin.register(PositieType)
class PositieTypeAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "naam",
        "status",
    )

    list_filter = ("status",)

    search_fields = ("uuid", "naam")

    readonly_fields = ("uuid",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "naam",
                    "omschrijving",
                    "status",
                    "startpositie",
                    "eindpositie",
                    "toelichting_inwoner",
                    "toelichting_medewerker",
                    "doelpositie",
                ),
            },
        ),
    )
