from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models.doel import Doel
from openplan.plannen.models.evaluatie import Evaluatie
from openplan.plannen.models.evaluatietype import Evaluatietype
from openplan.plannen.models.plan import Plan
from openplan.plannen.models.positie import Positie
from openplan.plannen.models.subdoel import SubDoel
from openplan.utils.fields import UUIDRelatedField

from .doel import NestedDoelSerializer

# from .evaluatietype import NestedEvaluatieSerializer
from .plan import NestedPlanSerializer


# TODO: Remove comments when other api's are implemented
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

    # evaluatietype = NestedEvaluatieSerializer(
    #     read_only=True,
    # )
    evaluatietype_uuid = UUIDRelatedField(
        queryset=Evaluatietype.objects.all(),
        write_only=True,
        source="evaluatietype",
        help_text=_("UUID van het type evaluatie."),
    )
    # posities = NestedPositieSerializer(
    #     read_only=True,
    #     many=True,
    # )
    positie_uuids = UUIDRelatedField(
        queryset=Positie.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="posities",
        help_text=_("UUID's van de posities die bij deze evaluatie horen."),
    )
    doelen = NestedDoelSerializer(
        read_only=True,
        many=True,
    )
    doel_uuids = UUIDRelatedField(
        queryset=Doel.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="doelen",
        help_text=_("UUID's van de doelen die bij deze evaluatie horen."),
    )
    # subdoelen = NestedSubdoelSerializer(
    #         read_only=True,
    #         many=True,
    #     )
    subdoel_uuids = UUIDRelatedField(
        queryset=SubDoel.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="subdoelen",
        help_text=_("UUID's van de subdoelen die bij deze evaluatie horen."),
    )

    class Meta:
        model = Evaluatie
        fields = [
            "uuid",
            "plan",
            "plan_uuid",
            # "evaluatietype",
            "evaluatietype_uuid",
            # "posities",
            "positie_uuids",
            "doelen",
            "doel_uuids",
            # "subdoelen",
            "subdoel_uuids",
            "naam",
            "omschrijving",
            "status",
            "datum",
            "contactmoment",
            "eigenaar",
            "zaak",
            "verslag",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
