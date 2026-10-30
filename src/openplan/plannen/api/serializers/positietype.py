from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.api.serializers.configuratie import NestedConfiguratieSerializer
from openplan.plannen.models import Configuratie, PositieType
from openplan.utils.fields import UUIDRelatedField


class NestedPositietypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositieType
        fields = [
            "uuid",
            "naam",
            "omschrijving",
            "status",
            "startpositie",
            "eindpositie",
            "toelichting_inwoner",
            "toelichting_medewerker",
            "doelpositie",
        ]

        extra_kwargs = {
            "uuid": {"read_only": True},
        }


class PositietypeSerializer(serializers.ModelSerializer):
    doelpositie = UUIDRelatedField(
        queryset=PositieType.objects.all(),
        required=False,
        allow_null=True,
        help_text=_("UUID van het bovenliggende doeltype (optioneel)."),
    )

    configuraties = NestedConfiguratieSerializer(many=True, read_only=True)
    configuratie_uuids = UUIDRelatedField(
        many=True,
        write_only=True,
        queryset=Configuratie.objects.all(),
        source="configuraties",
    )

    class Meta:
        model = PositieType
        fields = [
            "uuid",
            "configuraties",
            "configuratie_uuids",
            "naam",
            "omschrijving",
            "status",
            "startpositie",
            "eindpositie",
            "toelichting_inwoner",
            "toelichting_medewerker",
            "doelpositie",
        ]

        extra_kwargs = {
            "uuid": {"read_only": True},
        }
