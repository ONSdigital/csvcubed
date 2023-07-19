"""
Tests for friendly error messages being logged
"""
from pathlib import Path

from platformdirs import PlatformDirs

from csvcubed.cli.buildcsvw.build import _extract_and_validate_cube
from csvcubed.models.cube.cube import (
    ColumnNotFoundInDataError,
    Cube,
    DuplicateColumnTitleError,
    UriTemplateNameError,
)
from csvcubed.models.cube.qb.components.validationerrors import (
    EmptyQbMultiUnitsError,
    UndefinedAttributeValueUrisError,
    UndefinedMeasureUrisError,
    UndefinedUnitUrisError,
)
from csvcubed.models.cube.qb.validationerrors import (
    AttributeNotLinkedError,
    BothMeasureTypesDefinedError,
    BothUnitTypesDefinedError,
    DuplicateMeasureError,
    EmptyQbMultiMeasureDimensionError,
    HybridShapeError,
    LinkedObsColumnDoesntExistError,
    LinkedToNonObsColumnError,
    MoreThanOneMeasureColumnError,
    NoDimensionsDefinedError,
    NoMeasuresDefinedError,
    NoObservedValuesColumnDefinedError,
    NoUnitsDefinedError,
)
from csvcubed.models.cube.validationerrors import ObservationValuesMissing
from csvcubed.models.validationerror import (
    ConflictingUriSafeValuesError,
    ReservedUriValueError,
    ValidateModelPropertiesError,
)
from csvcubed.utils.cli import _write_errors_to_log
from tests.unit.test_baseunit import assert_num_validation_errors, get_test_cases_dir

_test_case_dir = Path(
    get_test_cases_dir().absolute(), "readers", "cube-config", "v1.0", "error_mappings"
)
_user_log_dir = Path(PlatformDirs("csvcubed_testing", "csvcubed").user_log_dir)
_log_file_path = _user_log_dir / "out.log"


def _assert_in_log(text: str) -> None:
    with open(_log_file_path) as log_file:
        contents = log_file.read()
    assert text in contents, contents


def test_val_errors_no_observation():
    """
    Test for:-
        NoObservedValuesColumnDefinedError
    """
    config = Path(_test_case_dir, "no_observed_values_column_defined_error.json")
    csv = Path(_test_case_dir, "no_observed_values_column_defined_error.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    # Check cube
    assert isinstance(cube, Cube)
    assert isinstance(cube.columns, list)
    assert len(cube.columns) == 3

    # Check returned errors
    assert isinstance(validation_errors, list)
    assert isinstance(validation_errors[0], NoObservedValuesColumnDefinedError)

    _assert_in_log(
        "ERROR - Validation Error: The cube does not contain an observed values "
        "column."
    )
    _assert_in_log(
        "ERROR - More information: http://purl.org/csv-cubed/err/no-obsv-col"
    )


def test_val_errors_no_measure():
    """
    Test for:-
        NoUnitsDefinedError
        NoMeasuresDefinedError
    """
    config = Path(_test_case_dir, "val_errors_no_measure.json")
    csv = Path(_test_case_dir, "val_errors_no_measure.csv")

    _, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 2)
    err_msgs = [
        "Found neither QbObservationValue.measure nor QbMultiMeasureDimension defined. One of these must be defined.",
        "Found neither QbObservationValue.unit nor QbMultiUnits defined. One of these must be defined.",
    ]
    for err in validation_errors:
        assert err.message in err_msgs

    assert isinstance(validation_errors[0], NoUnitsDefinedError)
    assert isinstance(validation_errors[1], NoMeasuresDefinedError)

    _assert_in_log(
        "ERROR - Validation Error: At least one unit must be defined in a cube."
    )
    _assert_in_log("ERROR - More information: http://purl.org/csv-cubed/err/no-unit")


def test_val_errors_col_not_in_data():
    """
    Test for:-
        ColumnNotFoundInDataError
    """
    config = Path(_test_case_dir, "column_not_found_in_data_error.json")
    csv = Path(_test_case_dir, "column_not_found_in_data_error.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)
    err_msgs = ["Column 'Dim-1' not found in data provided."]
    for err in validation_errors:
        assert err.message in err_msgs

    assert isinstance(validation_errors[0], ColumnNotFoundInDataError)
    _assert_in_log(
        "ERROR - Validation Error: Configuration found for column 'Dim-1' but no "
        "corresponding column found in CSV."
    )
    _assert_in_log(
        "ERROR - More information: http://purl.org/csv-cubed/err/col-not-found-in-dat"
    )


def test_val_errors_duplicate_col():
    """
    Test for:-
        DuplicateColumnTitleError
    """
    config = Path(_test_case_dir, "duplicate_column_title_error.json")
    csv = Path(_test_case_dir, "duplicate_column_title_error.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)
    assert validation_errors[0].message == "Duplicate column title 'Dim-2'"

    assert isinstance(validation_errors[0], DuplicateColumnTitleError)
    _assert_in_log(
        "ERROR - Validation Error: There are multiple CSV columns with the title: "
        "'Dim-2'."
    )
    _assert_in_log("ERROR - More information: http://purl.org/csv-cubed/err/dupe-col")


def test_val_errors_missing_obs_vals():
    """
    Test for:-
        ObservationValuesMissing
    """
    config = Path(_test_case_dir, "observation_values_missing.json")
    csv = Path(_test_case_dir, "observation_values_missing.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)
    assert (
        validation_errors[0].message
        == "Missing value(s) found for 'Amount' in row(s) 2, 3."
    )

    assert isinstance(validation_errors[0], ObservationValuesMissing)

    _assert_in_log(
        "ERROR - Validation Error: Observed values missing in 'Amount' on rows: "
        "{2, 3}"
    )
    _assert_in_log(
        "ERROR - More information: http://purl.org/csv-cubed/err/obsv-val-mis"
    )


def test_val_errors_both_measure_types():
    """
    Test for:-
        BothMeasureTypesDefinedError
    """
    config = Path(_test_case_dir, "both_measure_types_defined.json")
    csv = Path(_test_case_dir, "both_measure_types_defined.csv")

    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )

    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)

    assert isinstance(validation_errors[0], BothMeasureTypesDefinedError)
    _assert_in_log(
        "ERROR - Validation Error: Measures defined in multiple locations. Measures "
        "may only be defined in one location."
    )
    _assert_in_log(
        "Further details: A pivoted shape cube cannot have a measure dimension."
    )
    _assert_in_log(
        "ERROR - More information: http://purl.org/csv-cubed/err/both-meas-typ-def"
    )


def test_val_errors_both_unit_types():
    """
    Test for:-
        BothUnitTypesDefinedError
    """
    config = Path(_test_case_dir, "both_unit_types_defined.json")
    csv = Path(_test_case_dir, "both_unit_types_defined.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)

    assert isinstance(validation_errors[0], BothUnitTypesDefinedError)
    assert (
        validation_errors[0].message
        == "Both QbObservationValue.unit and QbMultiUnits have been defined. These "
        "components cannot be used together."
    )
    _assert_in_log(
        "ERROR - Validation Error: Units defined in multiple locations. Units may "
        "only be defined in one location."
    )
    _assert_in_log(
        "ERROR - More information: http://purl.org/csv-cubed/err/both-unit-typ-def"
    )


def test_val_errors_invalid_uri_template():
    """
    Test for:-
        UriTemplateNameError
    """
    config = Path(_test_case_dir, "invalid_uri_template.json")
    csv = Path(_test_case_dir, "invalid_uri_template.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)

    assert isinstance(validation_errors[0], UriTemplateNameError)

    _assert_in_log(
        "ERROR - Validation Error: Uri template: http://example.com/dimensions/{+not_a_column_name} is referencing a column that is not defined in the config. Currently defined columns are: dim_1, dim_2, amount, measure, units."
    )

    _assert_in_log(
        "ERROR - More information: http://purl.org/csv-cubed/err/missing-uri-template-name-error"
    )


def test_val_errors_more_than_one_measure():
    """
    Test for:-
        MoreThanOneMeasureColumnError,
    """
    config = Path(_test_case_dir, "more_than_one_measures_col.json")
    csv = Path(_test_case_dir, "more_than_one_measures_col.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)
    assert isinstance(validation_errors[0], MoreThanOneMeasureColumnError)
    assert (
        validation_errors[0].message
        == "Found 2 of QbMultiMeasureDimensions. Expected a maximum of 1."
    )
    _assert_in_log(
        "ERROR - Validation Error: Found 2 measures columns. Only 1 is permitted."
    )
    _assert_in_log(
        "ERROR - More information: http://purl.org/csv-cubed/err/multi-meas-col"
    )


def test_val_errors_undefined_attr_uri():
    """
    Test for:-
        UndefinedAttributeValueUrisError
    """
    config = Path(_test_case_dir, "undefined_attribute_value_uris.json")
    csv = Path(_test_case_dir, "undefined_attribute_value_uris.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)
    assert isinstance(validation_errors[0], UndefinedAttributeValueUrisError)

    _assert_in_log(
        "ERROR - Validation Error: The Attribute URI(s) {'beach-ware'} in the "
        "NewQbAttribute(label='My best attribute') attribute column have not been defined in the list of "
        "valid attribute values."
    )
    _assert_in_log(
        "ERROR - More information: http://purl.org/csv-cubed/err/undef-attrib"
    )


def test_val_errors_empty_multi_units():
    """
    Test for:-
        EmptyQbMultiUnitsError

    Where we have a QbMultiUnits but the units field
    is an empty list.
    """
    config = Path(_test_case_dir, "empty_unit_uris.json")
    csv = Path(_test_case_dir, "empty_unit_uris.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)
    assert isinstance(validation_errors[0], EmptyQbMultiUnitsError)

    _assert_in_log(
        "ERROR - Validation Error: A Unit column has been defined but no units have been defined within it"
    )

    _assert_in_log(
        "ERROR - More information: http://purl.org/csv-cubed/err/empty-multi-units"
    )


def test_val_errors_empty_multi_measure_dimension():
    """
    Test for:-
        EmptyQbMultiMeasureDimensionError

    Where we have a QbMultiMeasureDimension but the measures field
    is an empty list.
    """
    config = Path(_test_case_dir, "empty_measure_uris.json")
    csv = Path(_test_case_dir, "empty_measure_uris.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)
    assert isinstance(validation_errors[0], EmptyQbMultiMeasureDimensionError)

    _assert_in_log(
        "ERROR - Validation Error: A Measure column has been defined but no measures have been defined within it"
    )

    _assert_in_log(
        "ERROR - More information: http://purl.org/csv-cubed/err/empty-multi-meas-dimension"
    )


def test_val_errors_undefined_measure_uri():
    """
    Test for:-
        UndefinedMeasureUrisError

    Where the data contains an undefined measure uri
    """
    config = Path(_test_case_dir, "undefined_measure_uris.json")
    csv = Path(_test_case_dir, "undefined_measure_uris.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)
    assert isinstance(validation_errors[0], UndefinedMeasureUrisError)

    _assert_in_log(
        "ERROR - Validation Error: The Measure URI(s) {'Wage'} found in the data was not defined in the cube config."
    )

    _assert_in_log("ERROR - More information: http://purl.org/csv-cubed/err/undef-meas")


def test_val_errors_undefined_unit_uri():
    """
    Test for:-
        UndefinedUnitUrisError

    Where the data contains an undefined measure uri
    """
    config = Path(_test_case_dir, "undefined_unit_uris.json")
    csv = Path(_test_case_dir, "undefined_unit_uris.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)
    assert isinstance(validation_errors[0], UndefinedUnitUrisError)

    _assert_in_log(
        "ERROR - Validation Error: The Unit URI(s) {'Dollars'} found in the data was not defined in the cube config."
    )

    _assert_in_log("ERROR - More information: http://purl.org/csv-cubed/err/undef-unit")


def test_val_errors_uri_conflict():
    """
    Test for:-
        ConflictingUriSafeValuesError
    """
    config = Path(_test_case_dir, "conflicting_uri_safe_values.json")
    csv = Path(_test_case_dir, "conflicting_uri_safe_values.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)
    assert isinstance(validation_errors[0], ConflictingUriSafeValuesError)
    _assert_in_log(
        "ERROR - Validation Error: A URI collision has been detected in an attribute column."
    )
    _assert_in_log(
        "The values 'Software Sales', 'software-sales' map to the same URI-safe identifier 'software-sales'"
    )
    _assert_in_log(
        "ERROR - More information: https://purl.org/csv-cubed/err/conflict-uri"
    )


def test_val_errors_reserved_uri():
    """
    Test for:-
        ReservedUriValueError
    """
    config = Path(_test_case_dir, "reserved_uri_value_error.json")
    csv = Path(_test_case_dir, "reserved_uri_value_error.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)
    assert isinstance(validation_errors[0], ReservedUriValueError)

    assert (
        validation_errors[0].message
        == 'Label(s) "Code List" used in "NewQbCodeList" component. "code-list" is a reserved identifier and cannot '
        "be used in code-lists."
    )

    _assert_in_log(
        "ERROR - Validation Error: The URI value(s) ['Code List'] conflict with the reserved "
        "value: code-list'."
    )

    _assert_in_log(
        "ERROR - More information: https://purl.org/csv-cubed/err/resrv-uri-val"
    )


def test_val_errors_no_dimensions():
    """
    Test for:-
        NoDimensionsDefinedError
    """
    config = Path(_test_case_dir, "no_dimensions_defined.json")
    csv = Path(_test_case_dir, "no_dimensions_defined.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)
    assert isinstance(validation_errors[0], NoDimensionsDefinedError)

    assert (
        validation_errors[0].message
        == "At least 1 QbDimensions must be defined. Found 0."
    )

    _assert_in_log(
        "ERROR - Validation Error: The cube does not contain any dimensions, "
        "at least 1 dimension is required."
    )

    _assert_in_log("ERROR - More information: http://purl.org/csv-cubed/err/no-dim")


def test_duplicate_measure_error():
    """
    Test for:-
        DuplicateMeasureError
    """
    config = Path(_test_case_dir, "duplicate_measure_types_error.json")
    csv = Path(_test_case_dir, "duplicate_measure_types_error.csv")

    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )

    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)

    assert isinstance(validation_errors[0], DuplicateMeasureError)
    _assert_in_log(
        "In the pivoted shape, each observation value column must use a unique measure. Affected columns: Average Income, GDP"
    )


def test_attribute_not_linked_error():
    """
    Test for:-
        AttributeNotLinkedError
    """
    config = Path(_test_case_dir, "attribute_not_linked_error.json")
    csv = Path(_test_case_dir, "attribute_not_linked_error.csv")

    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )

    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)

    assert isinstance(validation_errors[0], AttributeNotLinkedError)
    _assert_in_log(
        "Unable to tell which observed values column 'Attribute' describes. Please set the `describes_observations` property in this column's configuration."
    )


def test_linked_obs_column_doesnt_exist_error():
    """
    Test for:-
        LinkedObsColumnDoesntExistError
    """
    config = Path(_test_case_dir, "linked_obs_column_doesnt_exist_error.json")
    csv = Path(_test_case_dir, "linked_obs_column_doesnt_exist_error.csv")

    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )

    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)

    assert isinstance(validation_errors[0], LinkedObsColumnDoesntExistError)
    _assert_in_log(
        "The 'Attribute' column has `describes_observations` set to 'Doesn't Exist'. The column does not appear to exist."
    )


def test_linked_to_non_obs_colums_error():
    """
    Test for:-
        LinkedToNonObsColumnError
    """
    config = Path(_test_case_dir, "linked_to_non_obs_column_error.json")
    csv = Path(_test_case_dir, "linked_to_non_obs_column_error.csv")

    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )

    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)

    assert isinstance(validation_errors[0], LinkedToNonObsColumnError)
    _assert_in_log(
        "The 'Attribute' column has `describes_observations` set to 'Location'. This column does not represent observed values."
    )


def test_hybrid_shape_error():
    """
    Test for:-
        HybridShapeError
    """
    config = Path(_test_case_dir, "hybrid_shape_error.json")
    csv = Path(_test_case_dir, "hybrid_shape_error.csv")

    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )

    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)

    assert isinstance(validation_errors[0], HybridShapeError)
    _assert_in_log(
        "Mutliple observation value columns have been at the same time as a standard shape measure column defined.",
    )


def test_validate_model_properties_error():
    """
    Test for:-
        ValidateModelPropertiesError
    """

    config = Path(_test_case_dir, "unit_only_scaling_factor.json")
    csv = Path(_test_case_dir, "unit_only_scaling_factor.csv")

    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )

    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert_num_validation_errors(validation_errors, 1)

    assert isinstance(validation_errors[0], ValidateModelPropertiesError)
    _assert_in_log(
        "ERROR - Validation Error: A value for si base unit conversion multiplier has been specified:",
    )
