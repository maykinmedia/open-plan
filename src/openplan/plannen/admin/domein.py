from django.contrib import admin

from ..models.domein import Domein


@admin.register(Domein)
class DomeinAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "naam",
        "omschrijving",
        "status",
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
                    "omschrijving",
                    "status",
                ),
            },
        ),
    )
