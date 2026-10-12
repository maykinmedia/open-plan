from django.contrib import admin

from ..models.evaluatie import Evaluatie


@admin.register(Evaluatie)
class EvaluatieAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "plan",
        "status",
        "datum",
    )
    list_filter = (
        "plan",
        "status",
    )
    search_fields = ("uuid",)
    readonly_fields = ("uuid",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "plan",
                    "evaluatie_type",
                    "status",
                    "datum",
                ),
            },
        ),
        (
            "Beschrijving",
            {
                "fields": (
                    "toelichting_status",
                    "notitie",
                ),
            },
        ),
        (
            "Relatie",
            {
                "fields": (
                    "eigenaar",
                    "contactpersoon",
                    "zaak",
                    "document",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("plan")
