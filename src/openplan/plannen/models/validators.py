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


def validate_positie_type_not_self(positie_type):
    parent = positie_type.doelpositie

    if parent and parent == positie_type:
        raise ValidationError(
            {"doelpositie": _("Een positie type kan niet naar zichzelf verwijzen.")}
        )

    while parent:
        if parent == positie_type:
            raise ValidationError(
                {
                    "doelpositie": _(
                        "Een doelpositie kan geen kind als bovenliggende positie hebben."
                    )
                }
            )
        parent = parent.doelpositie
