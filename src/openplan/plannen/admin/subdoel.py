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
    readonly_fields = ("uuid", "gewijzigd_op")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "doel",
                    "subdoeltype",
                    "naam",
                    "status",
                    "omschrijving",
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
                "fields": (
                    "reden_wijziging",
                    "toelichting_reden",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("doel", "subdoeltype")
