from django.contrib import admin

from ..models.evaluatietype import EvaluatieType


@admin.register(EvaluatieType)
class EvaluatieTypeAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "naam",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("naam", "uuid")
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
                ),
            },
        ),
    )
