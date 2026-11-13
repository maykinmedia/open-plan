from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
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


def validate_dates(start_datum: date | None, eind_datum: date | None) -> None:
    """
    Validate that `eind_datum` is after `start_datum`.

    Args:
        start_datum (date | None): The starting date.
        eind_datum (date | None): The ending date.

    Returns:
        None

    Raises:
        ValidationError: If both dates are provided and `eind_datum` <= `start_datum`.

    """
    if start_datum and eind_datum and eind_datum <= start_datum:
        raise ValidationError(
            _(
                "{eind_datum} mag niet op een eerdere of dezelfde dag vallen "
                "als de {start_datum}.".format(
                    eind_datum=str(eind_datum), start_datum=str(start_datum)
                )
            )
        )


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


nummer_validatie = RegexValidator(
    regex=r"^[0-9]+\Z",
    message=_("Dit veld mag alleen nummers bevatten."),
)
