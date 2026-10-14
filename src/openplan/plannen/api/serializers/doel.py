from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models.doel import Doel
from openplan.plannen.models.persoon import Persoon
from openplan.utils.fields import UUIDRelatedField

from .persoon import PersoonSerializer


class NestedDoelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doel
        fields = [
            "uuid",
            "status",
            "titel",
            "beschrijving",
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
    persoon = PersoonSerializer(
        read_only=True,
    )
    persoon_uuid = UUIDRelatedField(
        queryset=Persoon.objects.all(),
        write_only=True,
        source="persoon",
        help_text=_("UUID van de gekoppelde persoon."),
    )

    class Meta:
        model = Doel
        fields = [
            "uuid",
            "persoon",
            "persoon_uuid",
            "uuid",
            "status",
            "titel",
            "beschrijving",
            "startdatum",
            "einddatum",
            "resultaat",
            "reden_wijziging",
            "voortgang_toelichting",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
