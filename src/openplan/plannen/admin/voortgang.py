from django.contrib import admin

from ..models.voortgang import Voortgang


@admin.register(Voortgang)
class VoortgangAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "naam",
    )
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
                    "omschrijving",
                ),
            },
        ),
    )
