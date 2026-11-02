from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.fields import get_attribute


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
