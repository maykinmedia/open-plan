from django.contrib import admin

from ..models.subdoel import Subdoel


@admin.register(Subdoel)
class SubDoelAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "naam",
        "doel",
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
                    "doel",
                    "subdoeltype",
                    "status",
                    "omschrijving",
                ),
            },
        ),
        (
            "Data",
            {
                "fields": ("startdatum", "einddatum"),
            },
        ),
        (
            "Voortgang",
            {
                "fields": ("resultaat", "voortgang_toelichting"),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("doel")
