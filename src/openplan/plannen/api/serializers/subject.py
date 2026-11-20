from rest_framework import serializers

from openplan.plannen.models.subject import Subject


class NestedSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            "uuid",
            "profiel",
            "klant",
            "bsn",
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
            "brk",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
