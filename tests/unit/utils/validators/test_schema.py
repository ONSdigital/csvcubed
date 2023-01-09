from pathlib import Path

import appdirs
import pytest

from csvcubed.utils.validators.schema import (
    map_to_internal_validation_errors, validate_dict_against_schema)

_user_log_dir = Path(appdirs.AppDirs("csvcubed_testing", "csvcubed").user_log_dir)
_log_file_path = _user_log_dir / "out.log"


def _assert_in_log(text: str) -> None:
    with open(_log_file_path) as log_file:
        contents = log_file.read()
    assert text in contents, contents


def test_truncate_long_validation_error_message():
    schema = {
        "type": "object",
        "required": ["anEnumValue"],
        "properties": {
            "anEnumValue": {
                "type": "string",
                "enum": [
                    "https://example.com/one",
                    "https://example.com/two",
                    "https://example.com/three",
                    "https://example.com/four",
                    "https://example.com/five",
                    "https://example.com/six",
                    "https://example.com/seven",
                    "https://example.com/eight",
                    "https://example.com/nine",
                    "https://example.com/ten",
                ],
            }
        },
    }
    data = {"anEnumValue": "Not in enum"}

    json_validation_errors = validate_dict_against_schema(data, schema)

    assert len(json_validation_errors) == 1, [e.message for e in json_validation_errors]
    error = map_to_internal_validation_errors(schema, json_validation_errors)[0]

    assert error.json_path == "$.anEnumValue", error.json_path
    assert (
        error.to_display_string()
        == "$.anEnumValue - 'Not in enum' is not one of ['https://example.com/one', 'https://example.com/two', "
        "'https://example.com/three', 'https://example.com/four', 'https://…"
    )


def test_json_path_inside_array():
    schema = {
        "type": "object",
        "required": ["anArray"],
        "properties": {
            "anArray": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["anEnumValue"],
                    "properties": {"anEnumValue": {"type": "string", "enum": ["One"]}},
                },
            }
        },
    }
    data = {"anArray": [{"anEnumValue": "One"}, {"anEnumValue": "Not in enum"}]}

    json_validation_errors = validate_dict_against_schema(data, schema)

    assert len(json_validation_errors) == 1, [e.message for e in json_validation_errors]
    error = map_to_internal_validation_errors(schema, json_validation_errors)[0]

    assert error.json_path == "$.anArray[1].anEnumValue", error.json_path


def test_json_path_with_dots():
    schema = {
        "type": "object",
        "required": ["an.Enum.Value"],
        "properties": {"an.Enum.Value": {"type": "string", "enum": ["One"]}},
    }
    data = {"an.Enum.Value": "Not in enum"}

    json_validation_errors = validate_dict_against_schema(data, schema)

    assert len(json_validation_errors) == 1, [e.message for e in json_validation_errors]
    error = map_to_internal_validation_errors(schema, json_validation_errors)[0]

    assert error.json_path == "$.'an.Enum.Value'", error.json_path


def test_json_path_with_left_square_bracket():
    schema = {
        "type": "object",
        "required": ["an[Enum[Value"],
        "properties": {"an[Enum[Value": {"type": "string", "enum": ["One"]}},
    }
    data = {"an[Enum[Value": "Not in enum"}

    json_validation_errors = validate_dict_against_schema(data, schema)

    assert len(json_validation_errors) == 1, [e.message for e in json_validation_errors]
    error_message = map_to_internal_validation_errors(schema, json_validation_errors)[0]
    path_part = error_message.json_path

    assert path_part == "$.'an[Enum[Value'", path_part


def test_json_path_with_right_square_bracket():
    schema = {
        "type": "object",
        "required": ["an]Enum]Value"],
        "properties": {"an]Enum]Value": {"type": "string", "enum": ["One"]}},
    }
    data = {"an]Enum]Value": "Not in enum"}

    json_validation_errors = validate_dict_against_schema(data, schema)

    assert len(json_validation_errors) == 1, [e.message for e in json_validation_errors]
    error = map_to_internal_validation_errors(schema, json_validation_errors)[0]

    assert error.json_path == "$.'an]Enum]Value'", error.json_path


def test_json_path_with_spaces():
    schema = {
        "type": "object",
        "required": ["an Enum Value"],
        "properties": {"an Enum Value": {"type": "string", "enum": ["One"]}},
    }
    data = {"an Enum Value": "Not in enum"}

    json_validation_errors = validate_dict_against_schema(data, schema)

    assert len(json_validation_errors) == 1, [e.message for e in json_validation_errors]
    error = map_to_internal_validation_errors(schema, json_validation_errors)[0]

    assert error.json_path == "$.'an Enum Value'", error.json_path


def test_json_path_quote_escape():
    """Ensure that a quote character inside a path is escaped."""

    schema = {
        "type": "object",
        "required": ["an'Enum'Value"],
        "properties": {"an'Enum'Value": {"type": "string", "enum": ["One"]}},
    }
    data = {"an'Enum'Value": "Not in enum"}

    json_validation_errors = validate_dict_against_schema(data, schema)

    assert len(json_validation_errors) == 1, [e.message for e in json_validation_errors]
    error = map_to_internal_validation_errors(schema, json_validation_errors)[0]

    assert error.json_path == r"$.'an\'Enum\'Value'", error.json_path


def test_schema_validation_when_offline():
    """
    Ensures that a schema can be validated successfully when encountering connection errors,
    in this case the error is forced by giving a bad input url as the $ref.
    """
    schema = {
        "type": "object",
        "properties": {
            "publisher": {
                "description": "The publisher of the data set (uri)",
                "$ref": "http://thisisaurltoadocument/that/does/not/exist.json",
            },
        },
    }
    data = {
        "publisher": "https://www.gov.uk/government/organisations/youth-justice-board-for-england-and-wales"
    }

    json_validation_errors = validate_dict_against_schema(data, schema)
    _assert_in_log(
        "Could not resolve schema dependency. You may have internet connectivity problems."
    )
    _assert_in_log(
        "Unable to perform JSON Schema Validation. There may be undiscovered errors. Attempting to continue."
    )
    assert len(json_validation_errors) == 0


if __name__ == "__main__":
    pytest.main()
