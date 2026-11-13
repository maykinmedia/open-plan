from django.contrib import admin

from ..models.evaluatie import Evaluatie


@admin.register(Evaluatie)
class EvaluatieAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "plan",
        "naam",
        "status",
        "datum",
    )
    list_filter = ("status",)
    search_fields = ("uuid", "naam")
    readonly_fields = ("uuid",)
    filter_horizontal = ("posities", "doelen", "subdoelen")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "plan",
                    "evaluatietype",
                    "naam",
                    "omschrijving",
                    "status",
                    "datum",
                    "posities",
                    "doelen",
                    "subdoelen",
                ),
            },
        ),
        (
            "Relatie",
            {
                "fields": (
                    "eigenaar",
                    "contactmoment",
                    "zaak",
                    "verslag",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("plan", "evaluatietype")
            .prefetch_related("posities", "doelen", "subdoelen")
        )
