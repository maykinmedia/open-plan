from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models import Positie
from openplan.plannen.models.doel import Doel
from openplan.plannen.models.doeltype import DoelType
from openplan.utils.fields import UUIDRelatedField
from openplan.utils.history.serializers import (
    WIJZIGING_VELDEN,
    WijzigingSerializerMixin,
)

from .doeltype import NestedDoelTypeSerializer
from .validators import IsImmutableValidator, StartBeforeEndValidator


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
            "beoogde_startdatum",
            "beoogde_einddatum",
            "gewijzigd_op",
            "resultaat",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
            "gewijzigd_op": {"read_only": True},
        }


class DoelSerializer(WijzigingSerializerMixin, serializers.ModelSerializer):
    doeltype = NestedDoelTypeSerializer(
        read_only=True,
    )
    doeltype_uuid = UUIDRelatedField(
        queryset=DoelType.objects.all(),
        write_only=True,
        source="doeltype",
        help_text=_("UUID van de gekoppelde doeltype."),
        validators=[IsImmutableValidator()],
    )
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
            "doeltype",
            "doeltype_uuid",
            "status",
            "naam",
            "omschrijving",
            "startdatum",
            "einddatum",
            "beoogde_startdatum",
            "beoogde_einddatum",
            "gewijzigd_op",
            "resultaat",
        ] + list(WIJZIGING_VELDEN)
        extra_kwargs = {
            "uuid": {"read_only": True},
            "gewijzigd_op": {"read_only": True},
        }
        validators = [
            StartBeforeEndValidator("startdatum", "einddatum"),
            StartBeforeEndValidator("beoogde_startdatum", "beoogde_einddatum"),
        ]

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:
            fields["doeltype_uuid"].required = False
        return fields
