from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from vng_api_common.fields import URNField

from .validators import UUID_REGEX


class UuidURNField(URNField):
    """
    URN field (RFC 8141) that must end with `:uuid:<uuid>`.

    Extends the vng-api-common ``URNField`` with a check on the UUID suffix.
    """

    default_validators = [
        *URNField.default_validators,
        RegexValidator(
            f":uuid:{UUID_REGEX}$",
            _("Urn moet eindigen met `:uuid:<uuid>`."),
            code="urn_without_uuid",
        ),
    ]


@extend_schema_field(OpenApiTypes.UUID)
class UUIDRelatedField(serializers.RelatedField):
    """
    A read-write field that represents the target of the relationship
    by a unique 'uuid' attribute.
    """

    default_error_messages = {
        "does_not_exist": _("Object with uuid={value} does not exist."),
        "invalid": _("Invalid value."),
    }

    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            return queryset.get(uuid=data)
        except ObjectDoesNotExist:
            self.fail("does_not_exist", value=smart_str(data))
        except (TypeError, ValueError):
            self.fail("invalid")

    def to_representation(self, obj):
        return str(obj.uuid)
