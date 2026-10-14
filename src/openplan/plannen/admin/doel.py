from django.contrib import admin

from ..models.doel import Doel


@admin.register(Doel)
class DoelAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "titel",
        "persoon",
        "status",
        "startdatum",
    )
    list_filter = ("status",)
    search_fields = (
        "uuid",
        "titel",
    )
    readonly_fields = ("uuid",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "titel",
                    "persoon",
                    "status",
                    "beschrijving",
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

    # TODO: change to subject when possible
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("persoon")
