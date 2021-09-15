import pytest

import json
from csvqb.utils.jsonschemavalidation import validate_dict_against_schema_url


def test_json_schema_validation():
    value: dict = json.loads(
        """
        { "id" : "some string" }
        """
    )

    schema_url = (
        "https://github.com/GSS-Cogs/family-schemas/blob/main/dataset-schema-1.1.0.json"
    )

    validate_dict_against_schema_url(value, schema_url)
