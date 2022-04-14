"""
Tests for friendly error messages being logged
"""
import appdirs
from os import linesep
from pathlib import Path
from tempfile import TemporaryDirectory

from csvcubed.cli.build import build as cli_build
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
)

from csvcubed.models.cube.qb.components.validationerrors import ReservedUriValueError, ConflictingUriSafeValuesError, \
    UndefinedMeasureUrisError, UndefinedAttributeValueUrisError

from tests.unit.test_baseunit import get_test_cases_dir

TEST_CASE_DIR = Path(get_test_cases_dir().absolute(), "readers", "cube-config", "v1.0", "error_mappings")
LOG_FILEPATH = Path(appdirs.user_cache_dir(), "csvcubed_testing", "log", "out.log").resolve()


def _check_log(text: str) -> bool:
    with open(LOG_FILEPATH) as log_file:
        lines = log_file.readlines()
    for line in lines[::-1]:
        if text in line:
            return True
    return False


def test_01_val_errors_no_observation():
    """
    Test for:-
        NoObservedValuesColumnDefinedError
    """
    config = Path(TEST_CASE_DIR, "no_observed_values_column_defined_error.json")
    csv = Path(TEST_CASE_DIR, "no_observed_values_column_defined_error.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )

    # Check cube
    assert isinstance(cube, Cube)
    assert isinstance(cube.columns, list)
    assert len(cube.columns) == 3

    # Check returned errors
    assert isinstance(validation_errors, list)
    assert isinstance(validation_errors[0], NoObservedValuesColumnDefinedError)

    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: The cube does not contain an observed values "
                      "column.")
    assert _check_log("csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/no-obsv-col")


def test_02_val_errors_no_measure():
    """
    Test for:-
        NoUnitsDefinedError
        NoMeasuresDefinedError
    """
    config = Path(TEST_CASE_DIR, "val_errors_no_measure.json")
    csv = Path(TEST_CASE_DIR, "val_errors_no_measure.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 2
    err_msgs = [
        "Found neither QbObservationValue.measure nor QbMultiMeasureDimension defined. One of these must be defined.",
        'Found neither QbObservationValue.unit nor QbMultiUnits defined. One of these must be defined.'
    ]
    for err in validation_errors:
        assert err.message in err_msgs

    assert isinstance(validation_errors[0], NoUnitsDefinedError)
    assert isinstance(validation_errors[1], NoMeasuresDefinedError)

    assert _check_log('csvcubed.cli.build - ERROR - Validation Error: At least one unit must be defined in a cube.')
    assert _check_log('csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/no-unit')

    assert _check_log('svcubed.cli.build - ERROR - Validation Error: At least one measure must be defined in a cube.')
    assert _check_log('csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/no-meas')


def test_03_val_errors_col_not_in_data():
    """
    Test for:-
        ColumnNotFoundInDataError
    """
    config = Path(TEST_CASE_DIR, "column_not_found_in_data_error.json")
    csv = Path(TEST_CASE_DIR, "column_not_found_in_data_error.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )

    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    err_msgs = [
        "Column 'Dim-1' not found in data provided."
    ]
    for err in validation_errors:
        assert err.message in err_msgs

    assert isinstance(validation_errors[0], ColumnNotFoundInDataError)
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: Configuration found for column 'Dim-1' but no "
                      "corresponding column found in CSV.")
    assert _check_log("ERROR - More information: http://purl.org/csv-cubed/err/col-not-found-in-dat")


def test_04_val_errors_duplicate_col():
    """
    Test for:-
        DuplicateColumnTitleError
    """
    config = Path(TEST_CASE_DIR, "duplicate_column_title_error.json")
    csv = Path(TEST_CASE_DIR, "duplicate_column_title_error.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert validation_errors[0].message == "Duplicate column title 'Dim-2'"

    assert isinstance(validation_errors[0], DuplicateColumnTitleError)
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: There are multiple CSV columns with the title: "
                      "'Dim-2'.")
    assert _check_log("csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/dupe-col")


def test_05_val_errors_missing_obs_vals():
    """
    Test for:-
        ObservationValuesMissing
    """
    config = Path(TEST_CASE_DIR, "observation_values_missing.json")
    csv = Path(TEST_CASE_DIR, "observation_values_missing.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert validation_errors[0].message == "Missing value(s) found for 'Amount' in row(s) 2, 3."

    assert isinstance(validation_errors[0], ObservationValuesMissing)

    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: Observed values missing in 'Amount' on rows: "
                      "{2, 3}"
                      )
    assert _check_log("csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/obsv-val-mis")


def test_06_val_errors_both_measure_types():
    """
    Test for:-
        BothMeasureTypesDefinedError
    """
    config = Path(TEST_CASE_DIR, "both_measure_types_defined.json")
    csv = Path(TEST_CASE_DIR, "both_measure_types_defined.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out="validation_errors.json",
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert validation_errors[0].message == \
           'Both QbSingleMeasureObservationValue.measure and QbMultiMeasureDimension have been defined. These ' \
           'components cannot be used together. A single-measure cube cannot have a measure dimension.'

    assert isinstance(validation_errors[0], BothMeasureTypesDefinedError)
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: Measures defined in multiple locations. Measures "
                      "may only be defined in one location.")
    assert _check_log("Further details are: A single-measure cube cannot have a measure dimension.")
    assert _check_log("csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/both-meas-typ-def")


def test_07_val_errors_both_unit_types():
    """
    Test for:-
        BothUnitTypesDefinedError
    """
    config = Path(TEST_CASE_DIR, "both_unit_types_defined.json")
    csv = Path(TEST_CASE_DIR, "both_unit_types_defined.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1

    assert isinstance(validation_errors[0], BothUnitTypesDefinedError)
    assert validation_errors[0].message == "Both QbObservationValue.unit and QbMultiUnits have been defined. These " \
                                           "components cannot be used together."
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: Units defined in multiple locations. Units may "
                      "only be defined in one location.")
    assert _check_log("csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/both-unit-typ-def")


def test_08_val_errors_more_than_one_observation():
    """
    Test for:-
        MoreThanOneObservationsColumnError
    """
    config = Path(TEST_CASE_DIR, "more_than_one_observations_col.json")
    csv = Path(TEST_CASE_DIR, "more_than_one_observations_col.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], MoreThanOneObservationsColumnError)
    assert validation_errors[0].message == "Found 2 of QbObservationValues. Expected a maximum of 1."
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: Found 2 observed values columns. Only 1 is "
                      "permitted.")
    assert _check_log("csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/multi-obsv-col")


def test_09_val_errors_more_than_one_measure():
    """
    Test for:-
        MoreThanOneMeasureColumnError,
    """
    config = Path(TEST_CASE_DIR, "more_than_one_measures_col.json")
    csv = Path(TEST_CASE_DIR, "more_than_one_measures_col.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], MoreThanOneMeasureColumnError)
    assert validation_errors[0].message == "Found 2 of QbMultiMeasureDimensions. Expected a maximum of 1."
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: Found 2 measures columns. Only 1 is permitted.")
    assert _check_log("csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/multi-meas-col")


def test_10_val_errors_undefined_attr_uri():
    """
    Test for:-
        UndefinedAttributeValueUrisError
    """
    config = Path(TEST_CASE_DIR, "undefined_attribute_value_uris.json")
    csv = Path(TEST_CASE_DIR, "undefined_attribute_value_uris.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], UndefinedAttributeValueUrisError)
    assert validation_errors[0].message == "Found undefined value(s) for 'attribute value URI' of NewQbAttribute(" \
                                           "label='My best attribute'). Undefined values: {'beach-ware'}"
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: The Attribute URI {'beach-ware'} in column "
                      "'My best attribute' defined in the cube config was not found in the data.")
    assert _check_log("csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/undef-attrib")


def test_11_val_errors_undefined_measure_uri():
    """
    Test for:-
        UndefinedMeasureUrisError
    """
    config = Path(TEST_CASE_DIR, "undefined_measure_uris.json")
    csv = Path(TEST_CASE_DIR, "undefined_measure_uris.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], UndefinedMeasureUrisError)
    assert validation_errors[0].message == \
           "Found undefined value(s) for 'measure URI' of QbMultiMeasureDimension(" \
           "measures=[ExistingQbMeasure(measure_uri='https://example.org/measures/Billions'), " \
           "ExistingQbMeasure(measure_uri='https://example.org/measures/Bitcoin')]). " \
           "Undefined values: {'https://example.org/measures/billions', " \
           "'https://example.org/measures/bitcoin'}" or \
           validation_errors[0].message == \
           "Found undefined value(s) for 'measure URI' of QbMultiMeasureDimension(" \
           "measures=[ExistingQbMeasure(measure_uri='https://example.org/measures/Billions'), " \
           "ExistingQbMeasure(measure_uri='https://example.org/measures/Bitcoin')]). " \
           "Undefined values: {'https://example.org/measures/bitcoin', " \
           "'https://example.org/measures/billions'}"

    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: The Measure URI "
                      "{'https://example.org/measures/billions', 'https://example.org/measures/bitcoin'} found in the "
                      "data was not defined in the cube config.")
    assert _check_log("csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/undef-meas")


def test_12_val_errors_uri_conflict():
    """
    Test for:-
        ConflictingUriSafeValuesError
    """
    config = Path(TEST_CASE_DIR, "conflicting_uri_safe_values.json")
    csv = Path(TEST_CASE_DIR, "conflicting_uri_safe_values.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], ConflictingUriSafeValuesError)
    assert validation_errors[0].message == \
           f"Conflicting URIs: {linesep}    software-sales: 'software-sales', 'Software Sales'" or \
           validation_errors[0].message == \
           f"Conflicting URIs: {linesep}    software-sales: 'Software Sales', 'software-sales'"
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: A URI collision has been detected in: "
                      "'Attribute'.")
    assert _check_log("The values ('software-sales', 'Software Sales') all map to the same identifier "
                      "'software-sales'.") or \
           _check_log("The values ('Software Sales', 'software-sales') all map to the same identifier "
                      "'software-sales'.")
    assert _check_log("csvcubed.cli.build - ERROR - More information: https://purl.org/csv-cubed/err/conflict-uri")


def test_13_val_errors_reserved_uri():
    """
    Test for:-
        ReservedUriValueError
    """
    config = Path(TEST_CASE_DIR, "reserved_uri_value_error.json")
    csv = Path(TEST_CASE_DIR, "reserved_uri_value_error.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], ReservedUriValueError)

    assert validation_errors[0].message == \
           'Label(s) "Code List" used in "NewQbCodeList" component. "code-list" is a reserved identifier and cannot ' \
           'be used in code-lists.'

    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: The URI value(s) ['Code List'] conflict with the "
                      "reserved value: 'code-list'.")

    assert _check_log("csvcubed.cli.build - ERROR - More information: https://purl.org/csv-cubed/err/resrv-uri-val")


def test_14_val_errors_no_dimensions():
    """
    Test for:-
        NoDimensionsDefinedError
    """
    config = Path(TEST_CASE_DIR, "no_dimensions_defined.json")
    csv = Path(TEST_CASE_DIR, "no_dimensions_defined.csv")
    with TemporaryDirectory() as temp_dir_path:
        temp_dir = Path(temp_dir_path)
        output = temp_dir / "out"
        cube, validation_errors = cli_build(
            config_path=config,
            csv_path=csv,
            output_directory=output,
            validation_errors_file_out="validation_errors.json",
        )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], NoDimensionsDefinedError)

    assert validation_errors[0].message == \
           "At least 1 QbDimensions must be defined. Found 0."

    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: The cube does not contain any dimensions, "
                      "at least 1 dimension is required.")

    assert _check_log("csvcubed.cli.build - ERROR - More information: http://purl.org/csv-cubed/err/no-dim")


def test_15_val_errors_missing_col_def():
    """
    Test for:-
        MissingColumnDefinitionError
    Note: It is currently not possible to produce this error as a column in the data will be assumed to be a
        NewQbDimension if it is not defined in the cube config, so it appears in the list of cube columns which
        is used for the comparison.
    """
    pass