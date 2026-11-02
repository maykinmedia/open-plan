from rest_framework import serializers

from openplan.plannen.models.subject import Subject


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            "uuid",
            "plan",
            "status",
            "subjecttype",
            "rolbeschrijving",
            "profiel",
            "klant",
            "bsn",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
