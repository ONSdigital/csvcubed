import pytest

from csvcubed.utils.validators.schema import (
    validate_dict_against_schema,
    validation_error_to_message,
)


def test_truncate_long_validation_error_message():
    long_error_message_schema = {
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
    long_error_message_data = {"anEnumValue": "Not in enum"}

    json_validation_errors = validate_dict_against_schema(
        long_error_message_data, long_error_message_schema
    )

    assert len(json_validation_errors) == 1, [e.message for e in json_validation_errors]
    error_message = validation_error_to_message(json_validation_errors[0])
    [path_part, message_part] = error_message.split(" - ")

    assert path_part == "$.anEnumValue", path_part
    assert len(message_part) == 150, message_part
    assert (
        message_part
        == "'Not in enum' is not one of ['https://example.com/one', 'https://example.com/two', "
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
    error_message = validation_error_to_message(json_validation_errors[0])
    [path_part, _] = error_message.split(" - ")

    assert path_part == "$.anArray.[1].anEnumValue", path_part


def test_json_path_with_dots():
    schema = {
        "type": "object",
        "required": ["an.Enum.Value"],
        "properties": {"an.Enum.Value": {"type": "string", "enum": ["One"]}},
    }
    data = {"an.Enum.Value": "Not in enum"}

    json_validation_errors = validate_dict_against_schema(data, schema)

    assert len(json_validation_errors) == 1, [e.message for e in json_validation_errors]
    error_message = validation_error_to_message(json_validation_errors[0])
    [path_part, _] = error_message.split(" - ")

    assert path_part == "$.'an.Enum.Value'", path_part


def test_json_path_with_left_square_bracket():
    schema = {
        "type": "object",
        "required": ["an[Enum[Value"],
        "properties": {"an[Enum[Value": {"type": "string", "enum": ["One"]}},
    }
    data = {"an[Enum[Value": "Not in enum"}

    json_validation_errors = validate_dict_against_schema(data, schema)

    assert len(json_validation_errors) == 1, [e.message for e in json_validation_errors]
    error_message = validation_error_to_message(json_validation_errors[0])
    [path_part, _] = error_message.split(" - ")

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
    error_message = validation_error_to_message(json_validation_errors[0])
    [path_part, _] = error_message.split(" - ")

    assert path_part == "$.'an]Enum]Value'", path_part


def test_json_path_with_spaces():
    schema = {
        "type": "object",
        "required": ["an Enum Value"],
        "properties": {"an Enum Value": {"type": "string", "enum": ["One"]}},
    }
    data = {"an Enum Value": "Not in enum"}

    json_validation_errors = validate_dict_against_schema(data, schema)

    assert len(json_validation_errors) == 1, [e.message for e in json_validation_errors]
    error_message = validation_error_to_message(json_validation_errors[0])
    [path_part, _] = error_message.split(" - ")

    assert path_part == "$.'an Enum Value'", path_part


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
    error_message = validation_error_to_message(json_validation_errors[0])
    [path_part, _] = error_message.split(" - ")

    assert path_part == r"$.'an\'Enum\'Value'", path_part


if __name__ == "__main__":
    pytest.main()
