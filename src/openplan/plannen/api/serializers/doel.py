from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models.doel import Doel
from openplan.plannen.models.doeltype import DoelType
from openplan.plannen.models.plan import Plan
from openplan.plannen.models.subject import Subject
from openplan.utils.fields import UUIDRelatedField

from .doeltype import NestedDoelTypeSerializer
from .plan import NestedPlanSerializer
from .subject import SubjectSerializer


class NestedDoelSerializer(serializers.ModelSerializer):
    hoofd_doel = UUIDRelatedField(
        queryset=Doel.objects.all(),
        required=False,
        allow_null=True,
        help_text=_("UUID van de bovenliggende doel (optioneel)."),
    )

    class Meta:
        model = Doel
        fields = [
            "uuid",
            "status",
            "titel",
            "beschrijving",
            "startdatum",
            "einddatum",
            "resultaat",
            "toelichting_resultaat",
            "hoofd_doel",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }


class DoelSerializer(serializers.ModelSerializer):
    doeltype = NestedDoelTypeSerializer(
        read_only=True,
    )
    plannen = NestedPlanSerializer(
        many=True,
        read_only=True,
    )
    subject = SubjectSerializer(
        read_only=True,
    )

    doeltype_uuid = UUIDRelatedField(
        queryset=DoelType.objects.all(),
        write_only=True,
        source="doeltype",
        help_text=_("UUID van de gekoppelde doeltype."),
    )
    plannen_uuids = UUIDRelatedField(
        queryset=Plan.objects.all(),
        many=True,
        write_only=True,
        source="plannen",
        help_text=_("UUID van de plannen waaraan dit doel gekoppelt is."),
    )
    subject_uuid = UUIDRelatedField(
        queryset=Subject.objects.all(),
        write_only=True,
        source="Subject",
        help_text=_("UUID van de gekoppelde subject."),
    )
    hoofd_doel = UUIDRelatedField(
        queryset=Doel.objects.all(),
        required=False,
        allow_null=True,
        help_text=_("UUID van de bovenliggende doel (optioneel)."),
    )

    class Meta:
        model = Doel
        fields = [
            "uuid",
            "plannen",
            "plannen_uuids",
            "doeltype",
            "doeltype_uuid",
            "subject",
            "subject_uuid",
            "status",
            "titel",
            "beschrijving",
            "startdatum",
            "einddatum",
            "resultaat",
            "toelichting_resultaat",
            "hoofd_doel",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
