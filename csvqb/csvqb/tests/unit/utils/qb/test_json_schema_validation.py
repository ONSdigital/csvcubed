import pytest

import json
from csvqb.utils.jsonschemavalidation import validate_dict_against_schema_url


def test_json_schema_validation_passes():
    value: dict = json.loads(
        """
        { 
            "title" : "some title",
            "description" : "some description",
            "publisher" : "some publisher",
            "families" : ["some family"]
        }
        """
    )

    schema_url = "https://raw.githubusercontent.com/GSS-Cogs/family-schemas/main/dataset-schema-1.1.0.json"

    assert len(validate_dict_against_schema_url(value, schema_url)) == 0


def test_json_schema_validation_fails():
    value: dict = json.loads(
        """
        { 
            "title" : "some title",
            "description" : 3728,
            "publisher" : "some publisher",
            "families" : ["some family"]
        }
        """
    )

    schema_url = "https://raw.githubusercontent.com/GSS-Cogs/family-schemas/main/dataset-schema-1.1.0.json"

    assert len(validate_dict_against_schema_url(value, schema_url)) == 1
    assert str(
        validate_dict_against_schema_url(value, schema_url)[0]
        == "3728 is not of type 'string'"
    )
