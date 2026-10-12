from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models.evaluatie import Evaluatie
from openplan.plannen.models.plan import Plan
from openplan.utils.fields import UUIDRelatedField

from .plan import NestedPlanSerializer


class EvaluatieSerializer(serializers.ModelSerializer):
    plan = NestedPlanSerializer(
        read_only=True,
    )
    plan_uuid = UUIDRelatedField(
        queryset=Plan.objects.all(),
        write_only=True,
        source="plan",
        help_text=_("UUID van het plan waarbij deze evaluatie hoort."),
    )

    class Meta:
        model = Evaluatie
        fields = [
            "uuid",
            "evaluatie_type",
            "status",
            "datum",
            "toelichting_status",
            "notitie",
            "contactmoment",
            "eigenaar",
            "zaak",
            "document",
            "plan",
            "plan_uuid",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
