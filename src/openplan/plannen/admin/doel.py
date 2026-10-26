from django.contrib import admin

from ..models.doel import Doel


@admin.register(Doel)
class DoelAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "naam",
        "positie",
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
                    "positie",
                    "doeltype",
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
        return super().get_queryset(request).select_related("positie")
