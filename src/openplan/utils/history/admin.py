from django import forms
from django.contrib.admin.utils import flatten_fieldsets
from django.utils.translation import gettext_lazy as _

from simple_history.admin import SimpleHistoryAdmin

from openplan.plannen.enums.status import RedenWijziging

WIJZIGING_VELDEN = ("reden_wijziging", "toelichting_reden")


class WijzigingAdminForm(forms.ModelForm):
    """Reason fields only on the change form, not when adding."""

    reden_wijziging = forms.ChoiceField(
        label=_("Reden wijziging"),
        choices=[("", "---------")] + list(RedenWijziging.choices),
    )
    toelichting_reden = forms.CharField(
        label=_("Toelichting reden"),
        widget=forms.Textarea,
        required=False,
        max_length=1000,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance._state.adding:
            for veld in WIJZIGING_VELDEN:
                del self.fields[veld]


class WijzigingHistoryAdmin(SimpleHistoryAdmin):
    """
    Use as: @admin.register(Doel) class DoelAdmin(WijzigingHistoryAdmin)

    Adds a "History" button showing every state with its reason.
    If you define fieldsets, add "reden_wijziging" and "toelichting_reden".
    """

    form = WijzigingAdminForm
    history_list_display = list(WIJZIGING_VELDEN)

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj is None:  # add page: no reason fields
            fields = [f for f in fields if f not in WIJZIGING_VELDEN]
        return fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if obj is not None and not set(WIJZIGING_VELDEN) & set(
            flatten_fieldsets(fieldsets)
        ):
            fieldsets.append((_("Wijziging"), {"fields": WIJZIGING_VELDEN}))
        return fieldsets

    def save_model(self, request, obj, form, change):
        if change:
            obj._reden_wijziging = form.cleaned_data["reden_wijziging"]
            obj._toelichting_reden = form.cleaned_data.get("toelichting_reden", "")
        super().save_model(request, obj, form, change)
