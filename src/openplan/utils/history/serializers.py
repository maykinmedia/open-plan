from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.enums.status import RedenWijziging

from .models import WIJZIGING_VELDEN
from .signals import zet_wijziging

ZICHTBAAR_NA_VERWIJDEREN = ("versie_uuid", "uuid", *WIJZIGING_VELDEN)


class WijzigingSerializerMixin(serializers.Serializer):
    """
    Use as: class DoelSerializer(WijzigingSerializerMixin, serializers.ModelSerializer)

    reden_wijziging is required on update (PUT and PATCH), not on create.
    """

    reden_wijziging = serializers.ChoiceField(
        choices=RedenWijziging.choices,
        write_only=True,
        required=False,
        help_text=_("Reden van de wijziging. Verplicht bij wijzigen."),
    )
    toelichting_reden = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=1000,
        help_text=_("Toelichting op de reden van de wijziging."),
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance is not None and not attrs.get("reden_wijziging"):
            raise serializers.ValidationError(
                {"reden_wijziging": _("Een reden is verplicht bij wijzigen.")}
            )
        return attrs

    def create(self, validated_data):
        # No reason on create; the signal gives the history row REGISTREREN.
        self._pop_wijziging(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        reden, toelichting = self._pop_wijziging(validated_data)
        zet_wijziging(instance, reden, toelichting)
        return super().update(instance, validated_data)

    @staticmethod
    def _pop_wijziging(validated_data) -> tuple[str, str]:
        # Pop so they aren't passed to the model.
        return (
            validated_data.pop("reden_wijziging", ""),
            validated_data.pop("toelichting_reden", ""),
        )


class HistorieLijstSerializer(serializers.Serializer):
    """Short overview of one version: which one, of which object, and why."""

    versie_uuid = serializers.UUIDField(
        source="history_id",
        read_only=True,
        help_text=_("UUID van deze versie."),
    )
    uuid = serializers.UUIDField(
        read_only=True,
        help_text=_("UUID van het object."),
    )
    reden_wijziging = serializers.CharField(read_only=True)
    toelichting_reden = serializers.CharField(read_only=True)


class HistorieSerializer(serializers.ModelSerializer):
    """
    Base for history serializers. Shows the history_id column as versie_uuid
    (versieUuid in the API).

        class DoelHistorieSerializer(HistorieSerializer):
            class Meta:
                model = Doel.history.model
                fields = historie_velden(Doel)
    """

    versie_uuid = serializers.UUIDField(
        source="history_id",
        read_only=True,
        help_text=_("UUID van deze versie."),
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Deleted object: hide its data, keep only the version id and reason.
        if self.context.get("gemaskeerd"):
            for veld in data:
                if veld not in ZICHTBAAR_NA_VERWIJDEREN:
                    data[veld] = None
        return data


def historie_velden(model):
    """
    Fields for a history serializer: versie_uuid, the model's own fields,
    then the reason fields.
    """
    object_velden = [
        field.name
        for field in model.history.model._meta.fields
        if field.name not in WIJZIGING_VELDEN and not field.name.startswith("history_")
    ]
    return ["versie_uuid"] + object_velden + list(WIJZIGING_VELDEN)
