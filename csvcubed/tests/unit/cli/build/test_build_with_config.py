"""
CSV Cubed Error Hierarchy
[] denotes abstract class
* denotes reference to previously defined class

cube.validationerror
    ValidationError
        [PydanticValidationError]
            UnknownPydanticValidationError
    [PydanticThrowableSpecificValidationError]
    [SpecificValidationError]

cube.validation_errors
    * [SpecificValidationError]
        ColumnValidationError
        ColumnNotFoundInDataError - Done
        DuplicateColumnTitleError - Done
        MissingColumnDefinitionError - Not Possible to produce
        ObservationsValuesMissing - Done

cube.qb.validation_errors
    * [SpecificValidationError]
        CsvColumnUriTemplateMissing
        CsvColumnLiteralWithUriTemplate
        [IncompatibleComponentsError]
            BothMeasureTypesDefinedError
            BothUnitTypesDefinedError
        [WrongNumberComponentsError]
            -
        [NeitherDefinedError]
            NoMeasuresDefinedError - done test_02_02
            NoObservedValuesColumnDefinedError - done test_02_01
            NoUnitsDefinedError - done  test_02_02

        [MaxNumComponentsExceededError]
            MoreThanOneMeasureColumnError  - done test_02_09
            MoreThanOneObservationsColumnError -done test_02_08
            MoreThanOneUnitsColumnError  - done test_02_07

cube.qb.components.validation_errors
    * [PydanticThrowableSpecificValidationError]
        ReservedUriValueError test_02_13
        ConflictingUriSafeValuesError - done test_02_12

    * [SpecificValidationError]
        UndefinedUriCollisionError

        [UndefinedValuesError]
            UndefinedAttributeUrisError - done test_02_10
            UndefinedMeasureUrisError - done test_02_11
            UndefinedUnitUrisError - done test_02_07
"""

from pathlib import Path

import appdirs
import pytest

from csvcubed.cli.build import build as cli_build
from csvcubed.models.cube import (
    ColumnNotFoundInDataError,
    DuplicateColumnTitleError,
    ObservationValuesMissing,
    BothMeasureTypesDefinedError
)
from csvcubed.models.cube import Cube, MissingColumnDefinitionError
from csvcubed.models.cube.qb.components.validationerrors import UndefinedUnitUrisError, \
    UndefinedAttributeValueUrisError, UndefinedMeasureUrisError, ConflictingUriSafeValuesError, ReservedUriValueError
from csvcubed.models.cube.qb.validationerrors import (
    NoObservedValuesColumnDefinedError,
    NoUnitsDefinedError,
    NoMeasuresDefinedError,
    MoreThanOneUnitsColumnError,
    MoreThanOneMeasureColumnError,
    MoreThanOneObservationsColumnError
)
from tests.unit.test_baseunit import get_test_cases_dir

PROJECT_ROOT = Path(Path(__file__).parent, "..", "..", "..", "..").resolve()
TEST_CASE_DIR = Path(get_test_cases_dir().absolute(), 'cli', 'build')
SCHEMA_PATH_FILE = Path(PROJECT_ROOT, "csvcubed", "schema", "cube-config-schema.json")


def test_01_01_build_ok():
    config = Path(TEST_CASE_DIR, "cube_data_config_ok.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_config_ok.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 0


def test_01_02_build_ok_fail_on_error():
    config = Path(TEST_CASE_DIR, "cube_data_config_ok.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_config_ok.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
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
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_01.csv")
    with pytest.raises(SystemExit) as err:
        cube, validation_errors = cli_build(
            config_path=config,
            output_directory=output,
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
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_01.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    # Check cube
    assert isinstance(cube, Cube)
    assert isinstance(cube.columns, list)
    assert len(cube.columns) == 3

    # Check returned errors
    assert isinstance(validation_errors, list)
    assert isinstance(validation_errors[0], NoObservedValuesColumnDefinedError)

    # Check logged validation errors
    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert 'csvcubed.cli.build - ERROR - Validation Error: No column of observed values was found in the ' \
               'cube.\n' in lines[-2]
        assert 'Refer to http://purl.org/csv-cubed/err/no-obsv-col for guidance on correcting this problem.\n' in \
               lines[-1]
    # csvcubed.cli.build - ERROR - Validation Error: No column of observed values was found in the cube.\n


def test_02_02_val_errors_no_measure():
    """
    Test for:-
    NoUnitsDefinedError
    NoMeasuresDefinedError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_02.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_02.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
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

    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert 'csvcubed.cli.build - ERROR - Validation Error: No column of units was found in the cube.\n' in lines[-4]
        assert 'Refer to http://purl.org/csv-cubed/err/no-unit for guidance on correcting this problem.\n' in lines[-3]
        assert 'csvcubed.cli.build - ERROR - Validation Error: No column of measures was found in the cube.\n' in lines[-2]
        assert 'Refer to http://purl.org/csv-cubed/err/no-meas for guidance on correcting this problem.\n' in lines[-1]


def test_02_03_val_errors_col_not_in_data():
    """
    Test for:-
    ColumnNotFoundInDataError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_03.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_03.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
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

    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert "csvcubed.cli.build - ERROR - Validation Error: The cube configuration refers to the column 'Dim-1' " \
               "but no column in the data has this title.\n" in lines[-2]
        assert 'Refer to http://purl.org/csv-cubed/err/col-not-found-in-dat for guidance on correcting this problem.\n' in lines[-1]


def test_02_04_val_errors_duplicate_col():
    """
    Test for:-
    ColumnNotFoundInDataError
    NoMeasuresDefinedError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_04.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_04.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert validation_errors[0].message == "Duplicate column title 'Dim-2'"

    assert isinstance(validation_errors[0], DuplicateColumnTitleError)

    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert "csvcubed.cli.build - ERROR - Validation Error: There are multiple columns with the column title: " \
               "'Dim-2'.\n" in lines[-2]
        assert "Refer to http://purl.org/csv-cubed/err/dupe-col for guidance on correcting this problem.\n" in lines[-1]


def test_02_05_val_errors_missing_obs_vals():
    """
    Test for:-
    ObservationValuesMissing
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_05.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_05.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert validation_errors[0].message == "Missing value(s) found for 'Amount' in row(s) 2, 3."

    assert isinstance(validation_errors[0], ObservationValuesMissing)

    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert "csvcubed.cli.build - ERROR - Validation Error: Observation values are missing in the column: " \
               "'Amount' on rows: {2, 3}\n" in lines[-2]
        assert "Refer to http://purl.org/csv-cubed/err/obsv-val-mis for guidance on correcting this problem." in \
               lines[-1]


def test_02_06_val_errors_both_measure_types():
    """
    Test for:-
    BothMeasureTypesDefinedError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_06.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_06.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert validation_errors[0].message == "Found 2 of QbMultiMeasureDimensions. Expected a maximum of 1."

    assert isinstance(validation_errors[0], BothMeasureTypesDefinedError)

    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert "csvcubed.cli.build - ERROR - Validation Error: There are multiple columns with the column title: " \
               "'Dim-2'.\n" in lines[-2]
        assert "Refer to http://purl.org/csv-cubed/err/dupe-col for guidance on correcting this problem.\n" in lines[-1]


def test_02_07_val_errors_both_unit_types():
    """
    Test for:-
    UndefinedUnitUrisError
    MoreThanOneUnitsColumnError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_07.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_07.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 2

    assert isinstance(validation_errors[0], UndefinedUnitUrisError)
    assert isinstance(validation_errors[1], MoreThanOneUnitsColumnError)

    assert validation_errors[0].message == "Found undefined value(s) for 'unit URI' of QbMultiUnits(units=[NewQbUnit(" \
                                           "label='Pounds'), NewQbUnit(label='test-unit-2')]). Undefined values: {'dollars'}"
    assert validation_errors[1].message == "Found 2 of QbMultiUnits. Expected a maximum of 1."

    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert "csvcubed.cli.build - ERROR - Validation Error: The Unit URI {'dollars'} found in the data was not " \
               "defined in the cube config." in lines[-3]
        assert "Refer to http://purl.org/csv-cubed/err/undef-unit for guidance on correcting this problem." in lines[-2]
        assert "csvcubed.cli.build - ERROR - Validation Error: Found 2 of QbMultiUnits. Expected a maximum of 1." in \
               lines[-1]


def test_02_08_val_errors_more_than_one_observation():
    """
    Test for:-
    MoreThanOneObservationsColumnError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_08.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_08.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1
    assert isinstance(validation_errors[0], MoreThanOneObservationsColumnError)

    assert validation_errors[0].message == "Found 2 of QbObservationValue. Expected a maximum of 1."

    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert "csvcubed.cli.build - ERROR - Validation Error: The cube contained 2 columns of Observation values, " \
               "only 1 is permitted." in lines[-2]
        assert "Refer to http://purl.org/csv-cubed/err/multi-obsv-col for guidance on correcting this problem." in \
               lines[-1]


def test_02_09_val_errors_more_than_one_measure():
    """
    Test for:-
    MoreThanOneMeasureColumnError,
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_09.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_09.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1

    assert isinstance(validation_errors[0], MoreThanOneMeasureColumnError)

    assert validation_errors[0].message == "Found 2 of QbMultiMeasureDimension. Expected a maximum of 1."

    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert "csvcubed.cli.build - ERROR - Validation Error: The cube contained 2 columns of Measures, " \
               "only 1 is permitted." in lines[-2]
        assert "Refer to http://purl.org/csv-cubed/err/multi-meas-col for guidance on correcting this problem." in \
               lines[-1]


def test_02_10_val_errors_undefined_attr_uri():
    """
    Test for:-
    UndefinedAttributeValueUrisError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_10.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_10.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1

    assert isinstance(validation_errors[0], UndefinedAttributeValueUrisError)

    assert validation_errors[0].message == "Found undefined value(s) for 'attribute value URI' of NewQbAttribute(" \
                                           "label='My best attribute'). Undefined values: {'beach-ware'}"

    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert "csvcubed.cli.build - ERROR - Validation Error: The Attribute URI {'beach-ware'} in column 'My best " \
               "attribute' defined in the cube config was not found in the data" in lines[-2]
        assert "Refer to http://purl.org/csv-cubed/err/undef-attrib for guidance on correcting this problem." in \
               lines[-1]


def test_02_11_val_errors_undefined_measure_uri():
    """
    Test for:-
    UndefinedMeasureUrisError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_11.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_11.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1

    assert isinstance(validation_errors[0], UndefinedMeasureUrisError)

    assert validation_errors[0].message == \
           "Found undefined value(s) for 'measure URI' of QbMultiMeasureDimension(" \
           "measures=[NewQbMeasure(label='Billions'), NewQbMeasure(label='DogeCoin')]). Undefined values: {'bitcoin'}"

    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert "csvcubed.cli.build - ERROR - Validation Error: The Measure URI {'bitcoin'} found in the data was not " \
               "defined in the cube config." in lines[-2]
        assert "Refer to http://purl.org/csv-cubed/err/undef-meas for guidance on correcting this problem." in \
               lines[-1]


def test_02_12_val_errors_uri_conflict():
    """
    Test for:-
    ConflictingUriSafeValuesError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_12.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_12.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1

    assert isinstance(validation_errors[0], ConflictingUriSafeValuesError)

    assert validation_errors[0].message == \
           "Conflicting URIs: \r\n    software-sales: 'Software Sales', 'software-sales'"

    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert "csvcubed.cli.build - ERROR - Validation Error: Conflicting safe URI values were found when " \
               "validating the cube, in 'Attribute' column 'new attribute values'" in lines[-3]
        assert "The values {'Software Sales', 'software-sales'} all have the same safe-uri " in lines[-2]
        assert "Refer to https://purl.org/csv-cubed/err/conflict-uri for guidance on correcting this problem." in \
               lines[-1]


def test_02_13_val_errors_reserved_uri():
    """
    Test for:-
    ReservedUriValueError
    """
    config = Path(TEST_CASE_DIR, "cube_data_test_02_13.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_test_02_13.csv")
    cube, validation_errors = cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, list)
    assert len(validation_errors) == 1

    assert isinstance(validation_errors[0], ReservedUriValueError)

    assert validation_errors[0].message == \
           'Label(s) "Code List" used in "NewQbCodeList" component. "code-list" is a reserved identifier and cannot ' \
           'be used in code-lists.'

    log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
                        'out.log').resolve()
    with open(log_filepath) as log_file:
        lines = log_file.readlines()
        assert 'csvcubed.cli.build - ERROR - Validation Error: A Reserved-URI Value error occurred when validating ' \
               'the cube, Label(s) "Code List" used in "NewQbCodeList" component. "code-list" is a reserved ' \
               'identifier and cannot be used in code-lists..  The URI value(s) of \'[\'Code List\']\' conflicted ' \
               'with the reserved value: \'code-list\' in the code list values.' in lines[-2]
        assert "Refer to https://purl.org/csv-cubed/err/resrv-uri-val for guidance on correcting this problem." in \
               lines[-1]


def test_02_14_val_errors_missing_col_def():
    """
    Test for:-
    MissingColumnDefinitionError
    # Note: It is currently not possible to produce this error as a column in the data will be assumed to be a
    #     # NewQbDimension if it is not defined in the cube config, so it appears in the list of cube.columns which
    #     is used
    #     # for the comparision.
    #     # """
    #     # config = Path(TEST_CASE_DIR, "cube_data_test_02_14.json")
    #     # output = Path("./out")
    #     # csv = Path(TEST_CASE_DIR, "cube_data_test_02_14.csv")
    #     # cube, validation_errors = cli_build(
    #     #     config_path=config,
    #     #     output_directory=output,
    #     #     csv_path=csv,
    #     #     fail_when_validation_error_occurs=False,
    #     #     validation_errors_file_out=Path("validation_errors.json"),
    #     # )
    #     # assert isinstance(cube, Cube)
    #     # assert isinstance(validation_errors, list)
    #     # assert len(validation_errors) == 1
    #     #
    #     # assert isinstance(validation_errors[0], MissingColumnDefinitionError)
    #     #
    #     # assert validation_errors[0].message == \
    #     #        'Label(s) "Code List" used in "NewQbCodeList" component. "code-list" is a reserved identifier and
    #     cannot ' \
    #     #        'be used in code-lists.'
    #     #
    #     # log_filepath = Path(appdirs.user_log_dir(), '..', 'csvcubed', 'csvcubed_testing', 'Logs',
    #     #                     'out.log').resolve()
    #     # with open(log_filepath) as log_file:
    #     #     lines = log_file.readlines()
    #     #     assert 'csvcubed.cli.build - ERROR - Validation Error: A Reserved-URI Value error occurred when
    #     validating ' \
    #     #            'the cube, Label(s) "Code List" used in "NewQbCodeList" component. "code-list" is a reserved ' \
    #     #            'identifier and cannot be used in code-lists..  The URI value(s) of \'[\'Code List\']\'
    #     conflicted ' \
    #     #            'with the reserved value: \'code-list\' in the code list values.' in lines[-2]
    #     #     assert "Refer to https://purl.org/csv-cubed/err/resrv-uri-val for guidance on correcting this
    #     problem." in \
    #     #            lines[-1]

