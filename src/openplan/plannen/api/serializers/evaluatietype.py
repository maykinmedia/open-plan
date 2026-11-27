from rest_framework import serializers

from openplan.plannen.api.serializers.configuratie import NestedConfiguratieSerializer
from openplan.plannen.models import Configuratie, Evaluatietype
from openplan.utils.fields import UUIDRelatedField


class NestedEvaluatietypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluatietype
        fields = [
            "uuid",
            "naam",
            "omschrijving",
            "status",
            "toelichting_inwoner",
            "toelichting_medewerker",
        ]


class EvaluatietypeSerializer(serializers.ModelSerializer):
    configuraties = NestedConfiguratieSerializer(many=True, read_only=True)
    configuratie_uuids = UUIDRelatedField(
        many=True,
        write_only=True,
        queryset=Configuratie.objects.all(),
        source="configuraties",
    )

    class Meta:
        model = Evaluatietype
        fields = [
            "uuid",
            "configuraties",
            "configuratie_uuids",
            "naam",
            "omschrijving",
            "status",
            "toelichting_inwoner",
            "toelichting_medewerker",
        ]

        extra_kwargs = {
            "uuid": {"read_only": True},
        }
