"""
JSON Schema Validation
----------------------

Utils to help validate JSON against a Schema
"""
import jsonschema
import requests
import json

# from whatepackage import ValidationError  # fix this
from jsonschema.exceptions import ValidationError


def validate_dict_against_schema_url(
    value: dict, schema_url: str
) -> list[ValidationError]:
    schema: dict = json.loads(requests.get(schema_url).text)
    errors = []
    v = jsonschema.Draft7Validator(schema)
    err = sorted(v.iter_errors(value), key=lambda e: e.path)
    for error in err:
        errors.append(error)

    return errors
