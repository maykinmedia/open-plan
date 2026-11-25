from rest_framework import serializers

from openplan.plannen.models.subject import Subject

from .validators import SubjectVeldenValidator


class NestedSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            "uuid",
            "profiel",
            "klant",
            "bsn",
            "ruimtelijk_object",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            "uuid",
            "plan",
            "subjecttype",
            "profiel",
            "klant",
            "bsn",
            "ruimtelijk_object",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
        validators = [SubjectVeldenValidator()]
