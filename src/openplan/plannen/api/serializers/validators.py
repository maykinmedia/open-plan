from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import fields as drf_fields, serializers
from rest_framework.fields import get_attribute
from rest_framework.serializers import Serializer

from openplan.plannen.models.validators import validate_dates


def get_from_serializer_data_or_instance(
    field: str, data: dict, serializer: Serializer
) -> Any:
    serializer_field = serializer.fields[field]
    data_value = data.get(serializer_field.source, drf_fields.empty)
    if data_value is not drf_fields.empty:
        return data_value

    instance = serializer.instance
    if not instance:
        return None

    return serializer_field.get_attribute(instance)


class StartBeforeEndValidator:
    """
    Validate that start date is before the end date
    """

    code = "date-mismatch"
    message = _("De {} mag niet op een eerdere of dezelfde dag vallen als de {}.")
    requires_context = True

    def __init__(self, start_date_field, end_date_field):
        self.start_date_field = start_date_field
        self.end_date_field = end_date_field

    def __call__(self, attrs, serializer):
        start_date = get_from_serializer_data_or_instance(
            self.start_date_field, attrs, serializer
        )
        end_date = get_from_serializer_data_or_instance(
            self.end_date_field, attrs, serializer
        )
        try:
            validate_dates(start_date, end_date)
        except ValidationError:
            raise serializers.ValidationError(
                {
                    self.end_date_field: self.message.format(
                        self.end_date_field, self.start_date_field
                    ),
                },
                code=self.code,
            )


class IsImmutableValidator:
    """
    Validate that the field should not be changed in update action
    """

    message = _("This field can't be changed")
    code = "immutable-field"
    requires_context = True

    def __call__(self, new_value, serializer_field):
        instance = getattr(serializer_field.parent, "instance", None)
        # no instance -> it's not an update
        if not instance:
            return

        current_value = get_attribute(instance, serializer_field.source_attrs)

        if new_value != current_value:
            raise serializers.ValidationError(self.message, code=self.code)
