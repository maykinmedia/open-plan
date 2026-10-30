from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models import Positie, PositieType
from openplan.utils.fields import UUIDRelatedField

from .positietype import NestedPositietypeSerializer
from .subject import NestedSubjectSerializer


class NestedPositieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Positie
        fields = [
            "uuid",
            "naam",
            "omschrijving",
            "status",
            "reden_wijziging",
            "toelichting_reden",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }


class PositieSerializer(serializers.ModelSerializer):
    subject = NestedSubjectSerializer(
        read_only=True,
    )
    subject_uuid = UUIDRelatedField(
        queryset=PositieType.objects.all(),
        write_only=True,
        source="doeltype",
        help_text=_("UUID van het subject."),
    )
    positietype = NestedPositietypeSerializer(
        read_only=True,
    )
    positietype_uuid = UUIDRelatedField(
        queryset=PositieType.objects.all(),
        write_only=True,
        source="doeltype",
        help_text=_("UUID van de gekoppelde positietype."),
    )

    class Meta:
        model = Positie
        fields = [
            "uuid",
            "subject",
            "subject_uuid",
            "positietype",
            "positietype_uuid",
            "naam",
            "omschrijving",
            "status",
            "reden_wijziging",
            "toelichting_reden",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
