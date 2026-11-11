from django.contrib import admin

from ..models.evaluatietype import Evaluatietype


@admin.register(Evaluatietype)
class EvaluatietypeAdmin(admin.ModelAdmin):
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
                    "toelichting_inwoner",
                    "toelichting_medewerker",
                    "configuraties",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("configuraties")
