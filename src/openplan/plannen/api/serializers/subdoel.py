from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.models import Doel, Subdoel, SubdoelType
from openplan.utils.fields import UUIDRelatedField

from .doel import NestedDoelSerializer
from .subdoeltype import NestedSubdoeltypeSerializer
from .validators import IsActiveValidator, IsImmutableValidator, StartBeforeEndValidator


class NestedSubdoelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subdoel
        fields = [
            "uuid",
            "status",
            "naam",
            "omschrijving",
            "notitie_intern",
            "notitie_extern",
            "startdatum",
            "einddatum",
            "beoogde_startdatum",
            "beoogde_einddatum",
            "gewijzigd_op",
            "voortgang",
            "reden_wijziging",
            "toelichting_reden",
        ]
        extra_kwargs = {
            "uuid": {"read_only": True},
            "gewijzigd_op": {"read_only": True},
        }


class SubdoelSerializer(serializers.ModelSerializer):
    subdoeltype = NestedSubdoeltypeSerializer(
        read_only=True,
    )
    subdoeltype_uuid = UUIDRelatedField(
        queryset=SubdoelType.objects.all(),
        write_only=True,
        source="subdoeltype",
        help_text=_("UUID van het gekoppelde subdoeltype."),
        validators=[
            IsImmutableValidator(),
            IsActiveValidator(),
        ],
    )
    doel = NestedDoelSerializer(
        read_only=True,
    )
    doel_uuid = UUIDRelatedField(
        queryset=Doel.objects.all(),
        write_only=True,
        source="doel",
        help_text=_("UUID van het doel."),
    )

    class Meta:
        model = Subdoel
        fields = [
            "uuid",
            "doel",
            "doel_uuid",
            "subdoeltype",
            "subdoeltype_uuid",
            "status",
            "naam",
            "omschrijving",
            "notitie_intern",
            "notitie_extern",
            "startdatum",
            "einddatum",
            "beoogde_startdatum",
            "beoogde_einddatum",
            "gewijzigd_op",
            "voortgang",
            "reden_wijziging",
            "toelichting_reden",
        ]
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
            fields["subdoeltype_uuid"].required = False
        return fields
