from django.core.exceptions import ValidationError

from rest_framework import serializers

from openplan.plannen.models.validators import validate_dates


def get_from_serializer_data_or_instance(field, data, serializer):
    if field in data:
        return data[field]
    return getattr(serializer.instance, field, None)


class DateValidator:
    requires_context = True

    def __call__(self, value, serializer):
        startdatum = get_from_serializer_data_or_instance(
            "startdatum", value, serializer
        )
        einddatum = get_from_serializer_data_or_instance("einddatum", value, serializer)
        beoogde_startdatum = get_from_serializer_data_or_instance(
            "beoogde_startdatum", value, serializer
        )
        beoogde_einddatum = get_from_serializer_data_or_instance(
            "beoogde_einddatum", value, serializer
        )

        try:
            validate_dates(startdatum, einddatum, field="einddatum")
            validate_dates(
                beoogde_startdatum, beoogde_einddatum, field="beoogde_einddatum"
            )
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
