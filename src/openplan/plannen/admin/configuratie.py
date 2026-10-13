from django.contrib import admin

from ..models.configuratie import Configuratie


@admin.register(Configuratie)
class ConfiguratieAdmin(admin.ModelAdmin):
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
                    "domein",
                    "naam",
                    "omschrijving",
                    "status",
                    "eigenaar",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("domein")
