from rest_framework import serializers

from openplan.plannen.models.subject import Subject


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            "uuid",
            "plan",
            "status",
            "rolbeschrijving",
            "profiel",
            "klant",
            "bsn",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
