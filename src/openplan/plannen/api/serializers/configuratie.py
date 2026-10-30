from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models.configuratie import Configuratie
from openplan.plannen.models.domein import Domein
from openplan.utils.fields import UUIDRelatedField

from .domein import DomeinSerializer


class ConfiguratieSerializer(serializers.ModelSerializer):
    domein = DomeinSerializer(
        read_only=True,
    )
    domein_uuid = UUIDRelatedField(
        queryset=Domein.objects.all(),
        write_only=True,
        source="domein",
        help_text=_("UUID van het gekoppelde domein."),
    )

    class Meta:
        model = Configuratie
        fields = [
            "uuid",
            "domein",
            "domein_uuid",
            "naam",
            "omschrijving",
            "status",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
        }
