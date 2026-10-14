from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_hoofd_doel_not_self(doel):
    if doel.hoofd_doel and doel.hoofd_doel == doel:
        raise ValidationError(
            {"hoofd_doel": _("Een doel kan niet naar zichzelf verwijzen.")}
        )

    parent = doel.hoofd_doel
    while parent:
        if parent == doel:
            raise ValidationError(
                {
                    "hoofd_doel": _(
                        "Een hoofd doel kan geen kind als bovenliggende doel hebben."
                    )
                }
            )
        parent = parent.hoofd_doel
