from django import forms
from django.contrib import admin

from ..models.positietype import PositieType
from ..models.validators import validate_configuraties_zelfde_domein


class PositieTypeAdminForm(forms.ModelForm):
    class Meta:
        model = PositieType
        fields = [
            "naam",
            "omschrijving",
            "status",
            "configuraties",
            "startpositie",
            "eindpositie",
            "toelichting_inwoner",
            "toelichting_medewerker",
            "doelpositie",
        ]

    def clean(self):
        cleaned_data = super().clean()
        configuraties = cleaned_data.get("configuraties")
        if configuraties is not None:
            validate_configuraties_zelfde_domein(
                self.instance,
                configuraties.values_list("domein_id", flat=True),
            )
        return cleaned_data


@admin.register(PositieType)
class PositieTypeAdmin(admin.ModelAdmin):
    form = PositieTypeAdminForm
    list_display = (
        "uuid",
        "naam",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("uuid", "naam")
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
                    "startpositie",
                    "eindpositie",
                    "toelichting_inwoner",
                    "toelichting_medewerker",
                    "doelpositie",
                    "configuraties",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("configuraties")
