from django.contrib import admin

from ..models.subdoeltype import SubdoelType


@admin.register(SubdoelType)
class SubdoelTypeAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "naam",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("naam", "uuid")
    readonly_fields = ("uuid",)
    filter_horizontal = ("configuraties",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "naam",
                    "omschrijving",
                    "status",
                    "gewenst_resultaat",
                    "toelichting_inwoner",
                    "toelichting_medewerker",
                    "configuraties",
                ),
            },
        ),
    )
