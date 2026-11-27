from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models import Plan
from openplan.plannen.models.subject import Subject
from openplan.utils.fields import UUIDRelatedField

from .plan import PlanSerializer
from .validators import IsImmutableValidator, SubjectVeldenValidator


class SubjectSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(
        read_only=True,
    )
    plan_uuid = UUIDRelatedField(
        queryset=Plan.objects.all(),
        write_only=True,
        source="plan",
        help_text=_("UUID van het gekoppelde plan."),
        validators=[IsImmutableValidator()],
    )

    class Meta:
        model = Subject
        fields = [
            "uuid",
            "plan",
            "plan_uuid",
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


class SubjectUpdateSerializer(SubjectSerializer):
    def get_fields(self):
        fields = super().get_fields()
        fields["plan_uuid"].required = False
        return fields
