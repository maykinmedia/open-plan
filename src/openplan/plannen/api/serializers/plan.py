from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models.plan import Plan
from openplan.utils.serializers import URNModelSerializer

from .validators import DateValidator


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
            "urn",
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
            "zaak",
            "contactmoment",
            "eigenaar",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
            "urn": {
                "lookup_field": "uuid",
                "help_text": _("De Uniform Resource Name van de plan."),
            },
            "gewijzigd_op": {"read_only": True},
        }

        validators = [
            DateValidator(),
        ]
