from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from ..models.positietype import PositieType


class PositieTypeAdminForm(forms.ModelForm):
    class Meta:
        model = PositieType
        fields = [
            "naam",
            "omschrijving",
            "status",
            "domein",
            "configuraties",
            "startpositie",
            "eindpositie",
            "toelichting_inwoner",
            "toelichting_medewerker",
            "doelpositie",
        ]

    def clean(self):
        cleaned_data = super().clean()
        domein = cleaned_data.get("domein")
        configuraties = cleaned_data.get("configuraties")
        if domein and configuraties:
            try:
                self.instance.controleer_configuraties(configuraties, domein)
            except ValidationError as error:
                self.add_error(None, error)
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
                    "configuraties",
                    "domein",
                    "naam",
                    "omschrijving",
                    "status",
                    "startpositie",
                    "eindpositie",
                    "toelichting_inwoner",
                    "toelichting_medewerker",
                    "doelpositie",
                ),
            },
        ),
    )
