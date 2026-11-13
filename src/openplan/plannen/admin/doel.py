from django.contrib import admin

from openplan.utils.history.admin import WijzigingHistoryAdmin

from ..models.doel import Doel


@admin.register(Doel)
class DoelAdmin(WijzigingHistoryAdmin):
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
                "fields": (
                    "startdatum",
                    "einddatum",
                    "beoogde_startdatum",
                    "beoogde_einddatum",
                    "gewijzigd_op",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("positie")
