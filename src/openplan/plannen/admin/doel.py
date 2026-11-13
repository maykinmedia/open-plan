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
    readonly_fields = ("uuid", "gewijzigd_op")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "positie",
                    "doeltype",
                    "naam",
                    "omschrijving",
                    "status",
                    "notitie_intern",
                    "notitie_extern",
                    "voortgang",
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
                "fields": ("reden_wijziging", "toelichting_reden"),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("positie", "doeltype")
