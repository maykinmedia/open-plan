from rest_framework import serializers

from openplan.plannen.models.plan import Plan

from .validators import StartBeforeEndValidator


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "uuid",
            "naam",
            "omschrijving",
            "status",
            "startdatum",
            "einddatum",
            "beoogde_startdatum",
            "beoogde_einddatum",
            "gewijzigd_op",
            "tsaverwijzing",
            "zaak",
            "contactmoment",
            "eigenaar",
            "reden_wijziging",
            "toelichting_reden",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
            "gewijzigd_op": {"read_only": True},
        }

        validators = [
            StartBeforeEndValidator("startdatum", "einddatum"),
            StartBeforeEndValidator("beoogde_startdatum", "beoogde_einddatum"),
        ]
