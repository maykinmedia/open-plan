import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

UUID_REGEX = (
    "([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})"
)


def validate_charfield_entry(value, allow_apostrophe=False):
    """
    Validates a charfield entry according with Belastingdienst requirements.

    :param value: The input value string to be validated.
    :param allow_apostrophe: Boolean to add the apostrophe character to the
    validation. Apostrophes are allowed in input with ``True`` value. Defaults
    to ``False``.
    :return: The input value if validation passed. Otherwise, raises a
    ``ValidationError`` exception.
    """
    invalid_chars = '/"\\,;' if allow_apostrophe else "/\"\\,;'"

    for char in invalid_chars:
        if char in value:
            raise ValidationError(
                _("The provided value contains an invalid character: %s") % char
            )
    return value


def validate_phone_number(value):
    try:
        int(value.strip().lstrip("0+").replace("-", "").replace(" ", ""))
    except (ValueError, TypeError) as exc:
        raise ValidationError(_("Invalid mobile phonenumber.")) from exc

    return value


class CustomRegexValidator(RegexValidator):
    """
    CustomRegexValidator because the validated value is append to the message.
    """

    def __call__(self, value):
        """
        Validates that the input matches the regular expression.
        """
        if not self.regex.search(force_str(value)):
            message = f"{self.message}: {force_str(value)}"
            raise ValidationError(message, code=self.code)


validate_postal_code = CustomRegexValidator(
    regex="^[1-9][0-9]{3} ?[a-zA-Z]{2}$", message=_("Invalid postal code.")
)


@deconstructible
class URNValidator(RegexValidator):
    """
    The basic syntax for a URN is defined using the
    Augmented Backus-Naur Form (ABNF) as specified in [RFC5234].

    URN Syntax:

        namestring    = assigned-name
                        [ rq-components ]
                        [ "#" f-component ]

        assigned-name = "urn" ":" NID ":" NSS

        NID           = (alphanum) 0*30(ldh) (alphanum)
        ldh           = alphanum / "-"
        NSS           = pchar *(pchar / "/")

        rq-components = [ "?+" r-component ]
                        [ "?=" q-component ]
        r-component   = pchar *( pchar / "/" / "?" )
        q-component   = pchar *( pchar / "/" / "?" )

        f-component   = fragment

        ; general URI syntax rules (RFC3986)
        fragment      = *( pchar / "/" / "?" )
        pchar         = unreserved / pct-encoded / sub-delims / ":" / "@"
        pct-encoded   = "%" HEXDIG HEXDIG
        unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
        sub-delims    = "!" / "$" / "&" / "'" / "(" / ")" / "*" / "+" / "," / ";" / "="

        alphanum      = ALPHA / DIGIT  ; obsolete, usage is deprecated

    The question mark character "?" can be used without percent-encoding
    inside r-components, q-components, and f-components.  Other than
    inside those components, a "?" that is not immediately followed by
    "=" or "+" is not defined for URNs and SHOULD be treated as a syntax
    error by URN-specific parsers and other processors.

    https://datatracker.ietf.org/doc/html/rfc8141
    """

    HEXDIG = r"[0-9A-Fa-f]"
    ALPHANUM = r"[A-Za-z0-9]"
    pchar = rf"(?:{ALPHANUM}|[-._~]|%{HEXDIG}{HEXDIG}|[!$&'()*+,;=]|[:@])"

    # assigned-name
    NID = rf"{ALPHANUM}(?:{ALPHANUM}|-){{0,30}}{ALPHANUM}"
    NSS = rf"{pchar}(?:{pchar}|/)*"
    assigned_name = rf"urn:{NID}:{NSS}"

    # optional r/q components
    rq_components = (
        rf"(?:\?\+{pchar}(?:{pchar}|/|\?)*)?(?:\?={pchar}(?:{pchar}|/|\?)*)?"
    )

    # optional f-component
    f_component = rf"{pchar}(?:{pchar}|/|\?)*"

    # complete URN regex (RFC 8141)
    urn_pattern = rf"^{assigned_name}{rq_components}(?:#{f_component})?$"

    message = (
        "Enter a valid URN. Correct format: 'urn:<namespace>:<resource>' "
        "(e.g., urn:isbn:9780143127796)."
    )
    code = "invalid_urn"

    def __init__(self):
        super().__init__(
            regex=re.compile(self.urn_pattern),
            message=self.message,
            code=self.code,
        )
