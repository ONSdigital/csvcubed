from pathlib import Path

import appdirs
import pytest
from csvcubed.cli.build import build as cli_build

from csvcubed.models.cube import *
from csvcubed.models.cube.qb.components.validationerrors import *
from csvcubed.models.cube.qb.validationerrors import *
from tests.unit.test_baseunit import get_test_cases_dir

PROJECT_ROOT = Path(Path(__file__).parent, "..", "..", "..", "..").resolve()
TEST_CASE_DIR = Path(get_test_cases_dir().absolute(), 'cli', 'build')
LOG_FILEPATH = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs', 'out.log').resolve()


def _check_log(text: str) -> bool:
    with open(LOG_FILEPATH) as log_file:
        lines = log_file.readlines()
    for line in lines[::-1]:
        if text in line:
            return True
    return False


def test_01_01_build_ok():
    config = Path(TEST_CASE_DIR, "cube_data_config_ok.json")
    csv = Path(TEST_CASE_DIR, "cube_data_config_ok.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 0


def test_01_02_build_ok_fail_on_error():
    config = Path(TEST_CASE_DIR, "cube_data_config_ok.json")
    csv = Path(TEST_CASE_DIR, "cube_data_config_ok.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        fail_when_validation_error_occurs=True,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 0


def test_01_03_build_exit_on_fail():
    """
    Tests that the code exits on failure rather than returning incomplete cube with errors
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_01.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_01.csv")
    with pytest.raises(SystemExit) as err:
        cli_build(
            config_path=config,
            csv_path=csv,
            fail_when_validation_error_occurs=True,
            validation_errors_file_out=Path("validation_errors.json"),
        )
    assert err.value.code == 1


def test_02_01_val_errors_no_observation():
    """
    Test for:-
    NoObservedValuesColumnDefinedError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_01.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_01.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    # Check cube
    assert isinstance(cube, Cube)
    assert isinstance(cube.columns, list)
    assert len(cube.columns) == 3

    # Check returned errors
    assert isinstance(validation_errors, list)
    assert isinstance(validation_errors[0], NoObservedValuesColumnDefinedError)

    assert _check_log('csvcubed.cli.build - ERROR - Validation Error: The cube does not contain an Observed Values '
                      'column, this column type is required.')
    assert _check_log('Refer to http://purl.org/csv-cubed/err/no-obsv-col for guidance on correcting this problem.')


def test_02_02_val_errors_no_measure():
    """
    Test for:-
    NoUnitsDefinedError
    NoMeasuresDefinedError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_02.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_02.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
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

    assert _check_log('csvcubed.cli.build - ERROR - Validation Error: No column of units was found in the cube.')
    assert _check_log('Refer to http://purl.org/csv-cubed/err/no-unit for guidance on correcting this problem.')
    assert _check_log('csvcubed.cli.build - ERROR - Validation Error: No column of measures was found in the cube.')
    assert _check_log('Refer to http://purl.org/csv-cubed/err/no-meas for guidance on correcting this problem.')


def test_02_03_val_errors_col_not_in_data():
    """
    Test for:-
    ColumnNotFoundInDataError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_03.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_03.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
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
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: The cube configuration refers to the column "
                      "'Dim-1' but no column in the data has this title.")
    assert _check_log("Refer to http://purl.org/csv-cubed/err/col-not-found-in-dat for guidance on correcting this "
                      "problem.")


def test_02_04_val_errors_duplicate_col():
    """
    Test for:-
    ColumnNotFoundInDataError
    NoMeasuresDefinedError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_04.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_04.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert validation_errors[0].message == "Duplicate column title 'Dim-2'"

    assert isinstance(validation_errors[0], DuplicateColumnTitleError)
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: There are multiple columns with the column "
                      "title: 'Dim-2'.")
    assert _check_log("Refer to http://purl.org/csv-cubed/err/dupe-col for guidance on correcting this problem.")


def test_02_05_val_errors_missing_obs_vals():
    """
    Test for:-
    ObservationValuesMissing
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_05.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_05.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert validation_errors[0].message == "Missing value(s) found for 'Amount' in row(s) 2, 3."

    assert isinstance(validation_errors[0], ObservationValuesMissing)

    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: Observation values are missing in the column: " 
                      "'Amount' on rows: {2, 3}"
                      )
    assert _check_log("Refer to http://purl.org/csv-cubed/err/obsv-val-mis for guidance on correcting this problem.")


def test_02_06_val_errors_both_measure_types():
    """
    Test for:-
    BothMeasureTypesDefinedError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_06.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_06.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert validation_errors[0].message == \
           'Both QbSingleMeasureObservationValue.measure and QbMultiMeasureDimension have been defined. These ' \
           'components cannot be used together. A single-measure cube cannot have a measure dimension.'

    assert isinstance(validation_errors[0], BothMeasureTypesDefinedError)
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: Both measure types were present in the cube.")
    assert _check_log("The columns are 'QbSingleMeasureObservationValue.measure' and '<class "
                      "'csvcubed.models.cube.qb.components.measuresdimension.QbMultiMeasureDimension'>'")
    assert _check_log("Further details are: A single-measure cube cannot have a measure dimension.")
    assert _check_log("Refer to http://purl.org/csv-cubed/err/both-meas-typ-def for guidance on correcting this "
                      "problem.")


def test_02_07_val_errors_both_unit_types():
    """
    Test for:-
    UndefinedUnitUrisError
    MoreThanOneUnitsColumnError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_07.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_07.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1

    assert isinstance(validation_errors[0], BothUnitTypesDefinedError)
    assert validation_errors[0].message == "Both QbObservationValue.unit and QbMultiUnits have been defined. These " \
                                           "components cannot be used together."
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: Both unit types were present in the cube.")
    assert _check_log("The columns are 'QbObservationValue.unit' and '<class "
                      "'csvcubed.models.cube.qb.components.unitscolumn.QbMultiUnits'>'")
    assert _check_log("Refer to http://purl.org/csv-cubed/err/both-unit-typ-def for guidance on correcting this "
                      "problem.")


def test_02_08_val_errors_more_than_one_observation():
    """
    Test for:-
    MoreThanOneObservationsColumnError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_08.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_08.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], MoreThanOneObservationsColumnError)
    assert validation_errors[0].message == "Found 2 of QbObservationValue. Expected a maximum of 1."
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: The cube contained 2 columns of Observation "
                      "values, only 1 is permitted.")
    assert _check_log("Refer to http://purl.org/csv-cubed/err/multi-obsv-col for guidance on correcting this problem.")


def test_02_09_val_errors_more_than_one_measure():
    """
    Test for:-
    MoreThanOneMeasureColumnError,
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_09.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_09.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], MoreThanOneMeasureColumnError)
    assert validation_errors[0].message == "Found 2 of QbMultiMeasureDimension. Expected a maximum of 1."
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: The cube contained 2 columns of Measures, "
                      "only 1 is permitted.")
    assert _check_log("Refer to http://purl.org/csv-cubed/err/multi-meas-col for guidance on correcting this problem.")


def test_02_10_val_errors_undefined_attr_uri():
    """
    Test for:-
    UndefinedAttributeValueUrisError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_10.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_10.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], UndefinedAttributeValueUrisError)
    assert validation_errors[0].message == "Found undefined value(s) for 'attribute value URI' of NewQbAttribute(" \
                                           "label='My best attribute'). Undefined values: {'beach-ware'}"
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: The Attribute URI {'beach-ware'} in column 'My "
                      "best attribute' defined in the cube config was not found in the data")
    assert _check_log("Refer to http://purl.org/csv-cubed/err/undef-attrib for guidance on correcting this problem.")


def test_02_11_val_errors_undefined_measure_uri():
    """
    Test for:-
    UndefinedMeasureUrisError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_11.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_11.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], UndefinedMeasureUrisError)
    assert validation_errors[0].message == \
           "Found undefined value(s) for 'measure URI' of QbMultiMeasureDimension(" \
           "measures=[NewQbMeasure(label='Billions'), NewQbMeasure(label='DogeCoin')]). Undefined values: {'bitcoin'}"
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: The Measure URI {'bitcoin'} found in the data "
                      "was not defined in the cube config.")
    assert _check_log("Refer to http://purl.org/csv-cubed/err/undef-meas for guidance on correcting this problem.")


def test_02_12_val_errors_uri_conflict():
    """
    Test for:-
    ConflictingUriSafeValuesError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_12.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_12.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], ConflictingUriSafeValuesError)
    assert validation_errors[0].message == \
           "Conflicting URIs: \r\n    software-sales: 'software-sales', 'Software Sales'" or \
           validation_errors[0].message == \
           "Conflicting URIs: \r\n    software-sales: 'Software Sales', 'software-sales'"
    assert _check_log("csvcubed.cli.build - ERROR - Validation Error: Conflicting safe URI values were found when "
                      "validating the cube, in 'Attribute' column 'new attribute values'")
    assert _check_log("The values ('software-sales', 'Software Sales') all have the same safe-uri of "
                      "'software-sales' and the column labels were: ['software-sales'].") or \
           _check_log("The values ('Software Sales', 'software-sales') all have the same safe-uri of "
                      "'software-sales' and the column labels were: ['software-sales'].")
    assert _check_log("Refer to https://purl.org/csv-cubed/err/conflict-uri for guidance on correcting this problem.")


def test_02_13_val_errors_reserved_uri():
    """
    Test for:-
    ReservedUriValueError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_13.json")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_13.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        csv_path=csv,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], ReservedUriValueError)

    assert validation_errors[0].message == \
           'Label(s) "Code List" used in "NewQbCodeList" component. "code-list" is a reserved identifier and cannot ' \
           'be used in code-lists.'

    assert _check_log('csvcubed.cli.build - ERROR - Validation Error: A Reserved-URI Value error occurred when '
                      'validating the cube, Label(s) "Code List" used in "NewQbCodeList" component. "code-list" is a '
                      'reserved identifier and cannot be used in code-lists..  The URI value(s) of \'[\'Code '
                      'List\']\' conflicted with the reserved value: \'code-list\' in the code list values.')
    assert _check_log("Refer to https://purl.org/csv-cubed/err/resrv-uri-val for guidance on correcting this problem.")


def test_02_14_val_errors_missing_col_def():
    """
    Test for:-
    MissingColumnDefinitionError
    Note: It is currently not possible to produce this error as a column in the data will be assumed to be a
        NewQbDimension if it is not defined in the cube config, so it appears in the list of cube columns which
        is used for the comparison.
    """
    pass
