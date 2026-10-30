from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models.positietype import PositieType
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
    # TODO: ADD configuratie

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
