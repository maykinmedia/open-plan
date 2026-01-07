from django.contrib import admin

from openplan.plannen.models.version import Version


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ("plan", "actor", "comment", "created_at")
    list_filter = ("created_at", "actor", "plan")
    search_fields = ("plan__plantype__naam", "actor__username", "comment")
    readonly_fields = ("plan", "actor", "comment", "created_at", "snapshot")
    ordering = ("-created_at",)

    # Make the admin read-only
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
