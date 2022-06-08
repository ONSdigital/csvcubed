"""
Tests for friendly error messages being logged
"""
import appdirs
from pathlib import Path

from csvcubed.cli.build import (
    _extract_and_validate_cube,
    _write_errors_to_log,
)
from csvcubed.models.cube import (
    Cube,
    BothMeasureTypesDefinedError,
    BothUnitTypesDefinedError,
    ColumnNotFoundInDataError,
    DuplicateColumnTitleError,
    MoreThanOneMeasureColumnError,
    MoreThanOneObservationsColumnError,
    NoDimensionsDefinedError,
    NoMeasuresDefinedError,
    NoObservedValuesColumnDefinedError,
    NoUnitsDefinedError,
    ObservationValuesMissing,
    EmptyQbMultiMeasureDimensionError,
)


from csvcubed.models.cube.qb.components.validationerrors import (
    ReservedUriValueError,
    ConflictingUriSafeValuesError,
    UndefinedAttributeValueUrisError,
    UndefinedMeasureUrisError,
    UndefinedUnitUrisError,
    EmptyQbMultiUnitsError
)

from tests.unit.test_baseunit import get_test_cases_dir

_test_case_dir = Path(
    get_test_cases_dir().absolute(), "readers", "cube-config", "v1.0", "error_mappings"
)
_user_log_dir = Path(appdirs.AppDirs("csvcubed_testing", "csvcubed").user_log_dir)
_log_file_path = _user_log_dir / "out.log"


def _check_log(text: str) -> bool:
    with open(_log_file_path) as log_file:
        lines = log_file.readlines()
    for line in lines[::-1]:
        if text in line:
            return True
    return False


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

    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: The cube does not contain an observed values "
        "column."
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/no-obsv-col"
    )


def test_val_errors_no_measure():
    """
    Test for:-
        NoUnitsDefinedError
        NoMeasuresDefinedError
    """
    config = Path(_test_case_dir, "val_errors_no_measure.json")
    csv = Path(_test_case_dir, "val_errors_no_measure.csv")

    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 2
    err_msgs = [
        "Found neither QbObservationValue.measure nor QbMultiMeasureDimension defined. One of these must be defined.",
        "Found neither QbObservationValue.unit nor QbMultiUnits defined. One of these must be defined.",
    ]
    for err in validation_errors:
        assert err.message in err_msgs

    assert isinstance(validation_errors[0], NoUnitsDefinedError)
    assert isinstance(validation_errors[1], NoMeasuresDefinedError)

    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: At least one unit must be defined in a cube."
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/no-unit"
    )

    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: At least one measure must be defined in a cube."
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/no-meas"
    )


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
    assert len(validation_errors) == 1
    err_msgs = ["Column 'Dim-1' not found in data provided."]
    for err in validation_errors:
        assert err.message in err_msgs

    assert isinstance(validation_errors[0], ColumnNotFoundInDataError)
    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: Configuration found for column 'Dim-1' but no "
        "corresponding column found in CSV."
    )
    assert _check_log(
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
    assert len(validation_errors) == 1
    assert validation_errors[0].message == "Duplicate column title 'Dim-2'"

    assert isinstance(validation_errors[0], DuplicateColumnTitleError)
    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: There are multiple CSV columns with the title: "
        "'Dim-2'."
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/dupe-col"
    )


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
    assert len(validation_errors) == 1
    assert (
        validation_errors[0].message
        == "Missing value(s) found for 'Amount' in row(s) 2, 3."
    )

    assert isinstance(validation_errors[0], ObservationValuesMissing)

    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: Observed values missing in 'Amount' on rows: "
        "{2, 3}"
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/obsv-val-mis"
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
    assert len(validation_errors) == 1

    assert isinstance(validation_errors[0], BothMeasureTypesDefinedError)
    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: Measures defined in multiple locations. Measures "
        "may only be defined in one location."
    )
    assert _check_log(
        "Further details: A single-measure cube cannot have a measure dimension."
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/both-meas-typ-def"
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
    assert len(validation_errors) == 1

    assert isinstance(validation_errors[0], BothUnitTypesDefinedError)
    assert (
        validation_errors[0].message
        == "Both QbObservationValue.unit and QbMultiUnits have been defined. These "
        "components cannot be used together."
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: Units defined in multiple locations. Units may "
        "only be defined in one location."
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/both-unit-typ-def"
    )


def test_val_errors_more_than_one_observation():
    """
    Test for:-
        MoreThanOneObservationsColumnError
    """
    config = Path(_test_case_dir, "more_than_one_observations_col.json")
    csv = Path(_test_case_dir, "more_than_one_observations_col.csv")
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config, csv
    )
    _write_errors_to_log(json_schema_validation_errors, validation_errors)

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], MoreThanOneObservationsColumnError)
    assert (
        validation_errors[0].message
        == "Found 2 of QbObservationValues. Expected a maximum of 1."
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: Found 2 observed values columns. Only 1 is "
        "permitted."
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/multi-obsv-col"
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
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], MoreThanOneMeasureColumnError)
    assert (
        validation_errors[0].message
        == "Found 2 of QbMultiMeasureDimensions. Expected a maximum of 1."
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: Found 2 measures columns. Only 1 is permitted."
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/multi-meas-col"
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
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], UndefinedAttributeValueUrisError)

    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: The Attribute URI(s) {'beach-ware'} in the "
        "NewQbAttribute(label='My best attribute') attribute column have not been defined in the list of "
        "valid attribute values."
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/undef-attrib"
    )


def test_val_errors_empty_multi_units():
    """
    Test for:-
        EmptyQbMultiUnitsError

    Where we have a QbMultiMeasureDimension but the units field
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
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], EmptyQbMultiUnitsError)

    assert _check_log(
        "Validation Error: A validation error occurred when validating the cube: 'A units column must contain at least one defined unit'."
    )

    assert _check_log(
        "More information: http://purl.org/csv-cubed/err/empty-multi-units"
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
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], EmptyQbMultiMeasureDimensionError)

    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: A validation error occurred when validating the cube: 'A measure dimension must contain at least one defined measure'"
    )

    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/empty-multi-meas-dimension"
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
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], UndefinedMeasureUrisError)

    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: The Measure URI(s) {'Wage'} found in the data was not defined in the cube config."
    )

    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/undef-meas"
    )


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
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], UndefinedUnitUrisError)

    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: The Unit URI(s) {'Dollars'} found in the data was not defined in the cube config."
    )

    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/undef-unit"
    )


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
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], ConflictingUriSafeValuesError)
    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: A URI collision has been detected in an attribute column."
    )
    assert _check_log(
        "The values 'Software Sales', 'software-sales' map to the same URI-safe identifier 'software-sales'"
    ) or _check_log(
        "The values 'software-sales', 'Software Sales' map to the same URI-safe identifier 'software-sales'"
    )
    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: https://purl.org/csv-cubed/err/conflict-uri"
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
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], ReservedUriValueError)

    assert (
        validation_errors[0].message
        == 'Label(s) "Code List" used in "NewQbCodeList" component. "code-list" is a reserved identifier and cannot '
        "be used in code-lists."
    )

    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: The URI value(s) ['Code List'] conflict with the reserved "
        "value: code-list'."
    )

    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: https://purl.org/csv-cubed/err/resrv-uri-val"
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
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], NoDimensionsDefinedError)

    assert (
        validation_errors[0].message
        == "At least 1 QbDimensions must be defined. Found 0."
    )

    assert _check_log(
        "csvcubed.cli.build - ERROR - Validation Error: The cube does not contain any dimensions, "
        "at least 1 dimension is required."
    )

    assert _check_log(
        "csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/no-dim"
    )
