"""
JSON Schema Validation
----------------------

Utils to help validate JSON against a Schema
"""
import jsonschema
import requests
import json
import urllib.request
from urllib.request import urlopen

json_dict_representation: dict = json.loads(
    """
{
    "Hello": "World"
}
"""
)


def validate_dict_against_schema_url(value: dict, schema_url: str):
    # schema: dict = json.loads(requests.get(schema_url).text)

    # data = urllib.request.urlopen(schema_url).read().decode()
    # schema: dict = json.loads(data)

    response = urlopen(schema_url)
    schema = json.loads(response.read())
    return jsonschema.validate(value, schema)
