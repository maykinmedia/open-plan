from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import models
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from vng_api_common.validators import URNValidator

from .validators import UUID_REGEX


class URNField(models.CharField):
    """
    A custom Django model field to store a valid URN (RFC 8141: Uniform Resource Names)
    https://datatracker.ietf.org/doc/html/rfc8141

    This field extends CharField and automatically validates the value
    against a basic URN pattern: `urn:<namespace>:<resource>`.
    """

    default_validators = [
        URNValidator(),
        RegexValidator(
            f":uuid:{UUID_REGEX}$",
            _("Urn moet eindigen met `:uuid:<uuid>`."),
        ),
    ]
    description = _("URN")

    def __init__(self, *args, **kwargs):
        # Default max length 255 characters
        kwargs.setdefault("max_length", 255)
        super().__init__(*args, **kwargs)


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
