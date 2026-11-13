from django.contrib import admin

from ..models.subject import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("uuid", "subjecttype")
    search_fields = ("uuid",)
    readonly_fields = ("uuid",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "plan",
                    "subjecttype",
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
                    "brk",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("plan")
