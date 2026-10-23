from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models import Positie
from openplan.plannen.models.doel import Doel
from openplan.utils.fields import UUIDRelatedField


class NestedDoelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doel
        fields = [
            "uuid",
            "status",
            "naam",
            "omschrijving",
            "startdatum",
            "einddatum",
            "resultaat",
            "reden_wijziging",
            "voortgang_toelichting",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }


class DoelSerializer(serializers.ModelSerializer):
    # TODO: update when positie serializer is made
    # positie = PositieSerializer(
    #     read_only=True,
    # )
    positie_uuid = UUIDRelatedField(
        queryset=Positie.objects.all(),
        write_only=True,
        source="positie",
        help_text=_("UUID van de positie."),
    )

    class Meta:
        model = Doel
        fields = [
            "uuid",
            # "positie",
            "positie_uuid",
            "status",
            "naam",
            "omschrijving",
            "startdatum",
            "einddatum",
            "resultaat",
            "reden_wijziging",
            "voortgang_toelichting",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
