from rest_framework import serializers

from openplan.plannen.models.doeltype import DoelType


class NestedDoelTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoelType
        fields = ["uuid", "naam"]

        extra_kwargs = {
            "uuid": {"read_only": True},
        }


class DoelTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoelType
        fields = ["uuid", "naam", "omschrijving", "status", "gewenst_resultaat"]

        extra_kwargs = {
            "uuid": {"read_only": True},
        }
