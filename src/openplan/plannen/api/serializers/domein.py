from rest_framework import serializers

from openplan.plannen.models.domein import Domein


class DomeinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domein
        fields = [
            "uuid",
            "naam",
            "omschrijving",
            "status",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
