from django.db.models import ProtectedError, RestrictedError
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings


class ProtectedDestroyMixin:
    """
    Return a 400 instead of a 500 when deleting an object that is still
    referenced through on_delete=PROTECT or RESTRICT.
    """

    protected_error_message = _(
        "Dit object is nog in gebruik en kan niet verwijderd worden."
    )

    def perform_destroy(self, instance):
        try:
            super().perform_destroy(instance)
        except (ProtectedError, RestrictedError):
            raise ValidationError(
                {api_settings.NON_FIELD_ERRORS_KEY: [self.protected_error_message]}
            )
