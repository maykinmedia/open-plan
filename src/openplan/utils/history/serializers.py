from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from openplan.plannen.enums.status import RedenWijziging

# Add these to Meta.fields of every serializer that uses the mixin.
WIJZIGING_VELDEN = ("reden_wijziging", "toelichting_reden")


class WijzigingSerializerMixin(serializers.Serializer):
    """
    Use as: class DoelSerializer(WijzigingSerializerMixin, serializers.ModelSerializer)

    reden_wijziging is required on update (PUT and PATCH), not on create.
    """

    reden_wijziging = serializers.ChoiceField(
        choices=RedenWijziging.choices,
        write_only=True,
        required=False,
        help_text=_("Reden van de wijziging. Verplicht bij wijzigen."),
    )
    toelichting_reden = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=1000,
        help_text=_("Toelichting op de reden van de wijziging."),
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # DRF skips `required` on PATCH, so check it here.
        if self.instance is not None and not attrs.get("reden_wijziging"):
            raise serializers.ValidationError(
                {"reden_wijziging": _("Een reden is verplicht bij wijzigen.")}
            )
        return attrs


_cache = {}


def history_serializer_voor(model):
    """
    Read-only serializer for model.history, e.g. for Doel:

        {
          "redenWijziging": "wijzigen",
          "toelichtingReden": "Typfout",
          "uuid": "...",
          "naam": "...",
          ...
        }
    """
    history_model = model.history.model
    if history_model in _cache:
        return _cache[history_model]

    # The object's own fields, as they were after this change.
    object_velden = [
        field.name
        for field in history_model._meta.fields
        if field.name not in WIJZIGING_VELDEN and not field.name.startswith("history_")
    ]

    serializer = type(
        f"{model.__name__}HistorieSerializer",
        (serializers.ModelSerializer,),
        {
            "Meta": type(
                "Meta",
                (),
                {
                    "model": history_model,
                    "fields": list(WIJZIGING_VELDEN) + object_velden,
                },
            ),
        },
    )
    _cache[history_model] = serializer
    return serializer
