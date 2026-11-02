from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models import Positie
from openplan.plannen.models.doel import Doel
from openplan.plannen.models.doeltype import DoelType
from openplan.utils.fields import UUIDRelatedField

from .doeltype import NestedDoelTypeSerializer


class NestedDoelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doel
        fields = [
            "uuid",
            "status",
            "naam",
            "omschrijving",
            "startdatum",
            "einddatum",
            "resultaat",
            "reden_wijziging",
            "toelichting_reden",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }


class DoelSerializer(serializers.ModelSerializer):
    doeltype = NestedDoelTypeSerializer(
        read_only=True,
    )
    doeltype_uuid = UUIDRelatedField(
        queryset=DoelType.objects.all(),
        write_only=True,
        source="doeltype",
        help_text=_("UUID van de gekoppelde doeltype."),
    )
    # TODO: update when positie serializer is made
    # positie = PositieSerializer(
    #     read_only=True,
    # )
    positie_uuid = UUIDRelatedField(
        queryset=Positie.objects.all(),
        write_only=True,
        source="positie",
        help_text=_("UUID van de positie."),
    )

    class Meta:
        model = Doel
        fields = [
            "uuid",
            # "positie",
            "positie_uuid",
            "doeltype",
            "doeltype_uuid",
            "status",
            "naam",
            "omschrijving",
            "startdatum",
            "einddatum",
            "resultaat",
            "reden_wijziging",
            "toelichting_reden",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
