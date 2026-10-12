from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models.plan import Plan
from openplan.utils.serializers import URNModelSerializer


class NestedPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "uuid",
            "status",
            "naam",
            "beschrijving",
            "reden_wijziging",
            "voortgang_toelichting",
            "startdatum",
            "einddatum",
            "zaak",
            "contactmoment",
            "eigenaar",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }


class PlanSerializer(URNModelSerializer, serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "urn",
            "uuid",
            "status",
            "naam",
            "beschrijving",
            "reden_wijziging",
            "voortgang_toelichting",
            "startdatum",
            "einddatum",
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
        }
