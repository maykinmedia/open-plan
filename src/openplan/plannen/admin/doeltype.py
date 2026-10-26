from django.contrib import admin

from ..models.doeltype import DoelType


@admin.register(DoelType)
class DoelTypeAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "doel_type",
    )
    list_filter = ("doel_type",)
    search_fields = ("doel_type", "uuid")
    ordering = ("doel_type",)
    readonly_fields = ("uuid",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "doel_type",
                ),
            },
        ),
    )
