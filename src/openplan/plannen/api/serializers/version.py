from rest_framework import serializers

from openplan.plannen.models.version import Version


class VersionSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField()
    plan = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Version
        fields = [
            "id",
            "plan",
            "actor",
            "comment",
            "created_at",
            "snapshot",
        ]
        read_only_fields = fields
