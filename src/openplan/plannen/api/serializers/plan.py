from rest_framework import serializers
from vng_api_common.serializers import URNModelSerializer

from openplan.plannen.models.plan import Plan

from .validators import StartBeforeEndValidator


class NestedPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "uuid",
            "status",
            "naam",
            "omschrijving",
            "reden_wijziging",
            "toelichting_reden",
            "startdatum",
            "einddatum",
            "beoogde_startdatum",
            "beoogde_einddatum",
            "gewijzigd_op",
            "tsaverwijzing",
            "zaak",
            "contactmoment",
            "eigenaar",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
            "gewijzigd_op": {"read_only": True},
        }


class PlanSerializer(URNModelSerializer, serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "uuid",
            "status",
            "naam",
            "omschrijving",
            "reden_wijziging",
            "toelichting_reden",
            "startdatum",
            "einddatum",
            "beoogde_startdatum",
            "beoogde_einddatum",
            "gewijzigd_op",
            "tsaverwijzing",
            "zaak",
            "contactmoment",
            "eigenaar",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
            "gewijzigd_op": {"read_only": True},
        }

        validators = [
            StartBeforeEndValidator("startdatum", "einddatum"),
            StartBeforeEndValidator("beoogde_startdatum", "beoogde_einddatum"),
        ]
