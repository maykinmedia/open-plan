from jsonschema import Draft202012Validator

PRODUCTEN_SCHEMA = {
    "$schema": Draft202012Validator.META_SCHEMA["$id"],
    "title": "isGerelateerdAanSchema",
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "properties": {"urn": {"type": "string", "pattern": "^urn:.*$"}},
        "required": ["urn"],
    },
    "uniqueItems": True,
}
