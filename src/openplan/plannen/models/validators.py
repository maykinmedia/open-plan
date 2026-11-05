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


def validate_positie_type_not_self(positietype):
    parent = positietype.doelpositie

    if parent and parent == positietype:
        raise ValidationError(
            {"doelpositie": _("Een positie type kan niet naar zichzelf verwijzen.")}
        )

    while parent:
        if parent == positietype:
            raise ValidationError(
                {
                    "doelpositie": _(
                        "Een doelpositie kan geen kind als bovenliggende positie hebben."
                    )
                }
            )
        parent = parent.doelpositie


def validate_immutable_field(instance, field_name, message):
    """
    Raise a ValidationError if ``field_name`` on an existing object differs
    from the value stored in the database.
    """
    if instance._state.adding:
        return

    attname = instance._meta.get_field(field_name).attname
    huidige_waarde = (
        type(instance)
        .objects.filter(pk=instance.pk)
        .values_list(attname, flat=True)
        .first()
    )
    if huidige_waarde is not None and huidige_waarde != getattr(instance, attname):
        raise ValidationError({field_name: message})
