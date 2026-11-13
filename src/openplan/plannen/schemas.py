from jsonschema import Draft202012Validator
from vng_api_common.validators import URNValidator

from openplan.utils.validators import UUID_REGEX

PRODUCTEN_SCHEMA = {
    "$schema": Draft202012Validator.META_SCHEMA["$id"],
    "title": "isGerelateerdAanSchema",
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "urn": {
                "type": "string",
                "allOf": [
                    {
                        "pattern": URNValidator.urn_pattern,
                        "errorMessage": "'{value}' is geen geldige URN.",
                    },
                    {
                        "pattern": rf":uuid:{UUID_REGEX}$",
                        "errorMessage": "'{value}' moet eindigen op een UUID.",
                    },
                ],
            },
        },
        "required": ["urn"],
    },
    "uniqueItems": True,
}
