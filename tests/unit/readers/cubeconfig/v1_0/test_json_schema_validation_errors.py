from pathlib import Path
from typing import Optional

import pytest

from csvcubed.models.jsonvalidationerrors import JsonSchemaValidationError
from csvcubed.readers.cubeconfig.schema_versions import \
    get_deserialiser_for_schema
from tests.unit.test_baseunit import get_test_cases_dir

TEST_CASE_DIR = get_test_cases_dir().absolute() / "readers" / "cube-config" / "v1.0"


@pytest.mark.vcr
def test_json_schema_license_error_mapping():
    _assert_single_json_schema_validation_error_message(
        TEST_CASE_DIR / "schema_validation_errors" / "license_not_in_enum.json",
        "License 'http://example.com/some-license' is not recognised by csvcubed.",
    )


@pytest.mark.vcr
def test_json_schema_publisher_error_mapping():
    _assert_single_json_schema_validation_error_message(
        TEST_CASE_DIR / "schema_validation_errors" / "publisher_not_in_enum.json",
        "Publisher 'http://example.com/publisher' is not recognised by csvcubed.",
    )


@pytest.mark.vcr
def test_json_schema_creator_error_mapping():
    _assert_single_json_schema_validation_error_message(
        TEST_CASE_DIR / "schema_validation_errors" / "creator_not_in_enum.json",
        "Creator 'http://example.com/creator' is not recognised by csvcubed.",
    )


@pytest.mark.vcr
def test_json_schema_from_existing_dimension_error_mapping():
    error = _assert_single_json_schema_validation_error_message(
        TEST_CASE_DIR
        / "schema_validation_errors"
        / "from_existing_dim_not_in_enum.json",
        "Unable to identify {'type': 'dimension', 'label': 'Trade Direction Dimension', 'code_list': True, "
        "'from_existing': 'http://example.com/dimensions/trade-direction'}",
    )

    error_message = error.to_display_string(depth_to_display=3)

    assert (
        "$.from_existing - 'http://example.com/dimensions/trade-direction' is not recognised by csvcubed."
        in error_message
    )


@pytest.mark.vcr
def test_json_schema_from_existing_measure_error_deep_mapping():
    error = _assert_single_json_schema_validation_error_message(
        TEST_CASE_DIR
        / "schema_validation_errors"
        / "from_existing_meas_not_in_enum.json",
        "Unable to identify {'type': 'measures', 'values': [{'label': 'Monetary Value', 'from_existing': 'http://example.com/measure/monetary-value'}]}",
    )

    error_message = error.to_display_string(depth_to_display=3)

    assert (
        "$[0].from_existing - 'http://example.com/measure/monetary-value' is not recognised by csvcubed."
        in error_message
    )


@pytest.mark.vcr
def test_json_schema_validation_error_to_dict():
    error = _assert_single_json_schema_validation_error_message(
        TEST_CASE_DIR
        / "schema_validation_errors"
        / "from_existing_meas_not_in_enum.json"
    )
    dict = error.as_json_dict()
    assert "schema" not in dict

    # Ensure the functionality to remove the `schema` variable applies recursively to child errors.
    child_error = dict["possible_types_with_grouped_errors"][0][1][1]
    assert "message" in child_error
    assert "schema" not in child_error


def _assert_single_json_schema_validation_error_message(
    config_path: Path, expected_error_message: Optional[str] = None
) -> JsonSchemaValidationError:
    deserialiser = get_deserialiser_for_schema(None)
    csv_path = TEST_CASE_DIR / "schema_validation_errors" / "data.csv"
    _, json_schema_errors, _ = deserialiser(csv_path, config_path)
    assert len(json_schema_errors) == 1
    error = json_schema_errors[0]
    if expected_error_message is not None:
        assert error.message == expected_error_message

    return error


if __name__ == "__main__":
    pytest.main()
