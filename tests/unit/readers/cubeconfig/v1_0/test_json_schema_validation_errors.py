from pathlib import Path
from typing import Optional, Set

import pytest

from csvcubed.models.jsonvalidationerrors import (
    JsonSchemaValidationError,
    AnyOneOfJsonSchemaValidationError,
)
from csvcubed.readers.cubeconfig.schema_versions import get_deserialiser_for_schema
from csvcubed.utils.iterables import first
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
    child_error = dict["possible_types_with_grouped_errors"][0][1][0]
    assert "message" in child_error
    assert "schema" not in child_error


@pytest.mark.vcr
def test_qube_config_columns_filtered_by_type():
    """
    Ensure that qube-config.json errors in column definitions are filtered by the `type` specified in the config file.
    """
    deserialiser = get_deserialiser_for_schema(None)
    _, json_schema_errors, _ = deserialiser(
        TEST_CASE_DIR / "schema_validation_errors" / "data.csv",
        TEST_CASE_DIR
        / "schema_validation_errors"
        / "all_column_types_badly_defined.json",
    )

    def assert_column_error_has_possible_types(
        column_title: str, expected_possible_schema_type_refs: Set[str]
    ):
        error_for_column = first(
            json_schema_errors, lambda e: e.json_path == f"$.columns.{column_title}"
        )
        assert isinstance(error_for_column, AnyOneOfJsonSchemaValidationError)
        actual_possible_schema_type_refs = {
            possible_schema_type.get("$ref")
            for (
                possible_schema_type,
                _,
            ) in error_for_column.possible_types_with_grouped_errors
        }

        assert actual_possible_schema_type_refs == expected_possible_schema_type_refs

    # Expecting errors in `Dim-0`, `Dim-1`, `Attr-1`, `Amount`, `Measure` & `Units` columns.
    assert len(json_schema_errors) == 6

    assert_column_error_has_possible_types(
        "Dim-0", {"#/definitions/v1.0/columnTypes/Dimension"}
    )
    assert_column_error_has_possible_types(
        "Attr-1",
        {
            "#/definitions/v1.0/columnTypes/Attribute_Resource_New",
            "#/definitions/v1.0/columnTypes/Attribute_Resource_Existing",
            "#/definitions/v1.0/columnTypes/Attribute_Literal",
        },
    )
    assert_column_error_has_possible_types(
        "Amount", {"#/definitions/v1.0/columnTypes/Observations"}
    )
    assert_column_error_has_possible_types(
        "Measure",
        {
            "#/definitions/v1.0/columnTypes/Measures_New",
            "#/definitions/v1.0/columnTypes/Measures_Existing",
        },
    )
    assert_column_error_has_possible_types(
        "Units",
        {
            "#/definitions/v1.0/columnTypes/Units_New",
            "#/definitions/v1.0/columnTypes/Units_Existing",
        },
    )

    # Assert that Dim-1 which doesn't have `type` specified at all brings back all of the column definition types.
    assert_column_error_has_possible_types(
        "Dim-1",
        {
            None,  # This represents the `false` boolean which is defined inline without using `$ref`.
            "#/definitions/v1.0/columnTypes/Attribute_Literal",
            "#/definitions/v1.0/columnTypes/Attribute_Resource_Existing",
            "#/definitions/v1.0/columnTypes/Attribute_Resource_New",
            "#/definitions/v1.0/columnTypes/Dimension",
            "#/definitions/v1.0/columnTypes/Measures_Existing",
            "#/definitions/v1.0/columnTypes/Measures_New",
            "#/definitions/v1.0/columnTypes/Observations",
            "#/definitions/v1.0/columnTypes/Units_Existing",
            "#/definitions/v1.0/columnTypes/Units_New",
        },
    )


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
