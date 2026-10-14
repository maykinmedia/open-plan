from django.contrib import admin

from ..models.subject import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("uuid", "status")
    search_fields = ("uuid",)
    readonly_fields = ("uuid",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "plan",
                    "status",
                    "rolbeschrijving",
                ),
            },
        ),
        (
            "URNs",
            {
                "fields": (
                    "profiel",
                    "klant",
                    "bsn",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("plan")
