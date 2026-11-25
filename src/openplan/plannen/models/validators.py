from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from ..enums.status import SubjectType

if TYPE_CHECKING:
    from .positietype import PositieType


def validate_doelpositie_chain(
    positie_type: PositieType, doelpositie: PositieType | None
) -> None:
    seen: set[UUID] = set()
    current = doelpositie
    while current is not None and current.uuid not in seen:
        if current == positie_type:
            raise ValidationError(
                {
                    "doelpositie": _(
                        "Een positietype kan niet (via andere positietypen) naar "
                        "zichzelf verwijzen."
                    )
                }
            )
        seen.add(current.uuid)
        current = current.doelpositie


def validate_positie_type_not_self(positie_type: PositieType) -> None:
    validate_doelpositie_chain(positie_type, positie_type.doelpositie)


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


def validate_subject_velden(
    subjecttype: str,
    klant: str | None,
    bsn: str | None,
    ruimtelijk_object: str | None,
) -> None:
    """
    Validate the fields per subjecttype:
    - persoon: klant and/or bsn is required, ruimtelijk_object is not allowed
    - fysiek_object: ruimtelijk_object is required, klant and bsn are not allowed
    """
    errors = {}

    if subjecttype == SubjectType.PERSOON:
        if not (klant or bsn):
            msg = _("Bij subjecttype 'persoon' is een klant of BSN verplicht.")
            errors["klant"] = msg
            errors["bsn"] = msg
        if ruimtelijk_object:
            errors["ruimtelijk_object"] = _(
                "Bij subjecttype 'persoon' mag geen ruimtelijk object worden opgegeven."
            )

    elif subjecttype == SubjectType.FYSIEK_OBJECT:
        if not ruimtelijk_object:
            errors["ruimtelijk_object"] = _(
                "Bij subjecttype 'fysiek_object' is een ruimtelijk object verplicht."
            )
        msg = _(
            "Bij subjecttype 'fysiek_object' mag geen klant of BSN worden opgegeven."
        )
        if klant:
            errors["klant"] = msg
        if bsn:
            errors["bsn"] = msg

    if errors:
        raise ValidationError(errors)


nummer_validatie = RegexValidator(
    regex=r"^[0-9]+\Z",
    message=_("Dit veld mag alleen nummers bevatten."),
)
