import os
import pytest
from csvcubed.cli.build import build as cli_build
from csvcubed.readers.configdeserialiser import *
from tests.unit.test_baseunit import get_test_cases_dir
from csvcubed.cli.build import build

PROJECT_ROOT = Path(Path(__file__).parent, "..", "..", "..", "..").resolve()
TEST_CASE_DIR = Path(get_test_cases_dir().absolute(), "config")
SCHEMA_PATH_FILE = Path(PROJECT_ROOT, "csvcubed", "schema", "cube-config-schema.json")


def test_build_with_fail():
    config = Path(TEST_CASE_DIR, "cube_data_config_extra_cols.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_config_extra_cols.csv")
    with pytest.raises(SystemExit):
        cli_build(
            config=config,
            output_directory=output,
            csv_path=csv,
            fail_when_validation_error_occurs=True,
            validation_errors_file_out=Path(output, "validation_errors.json"),
        )


def test_build_without_fail():
    config = Path(TEST_CASE_DIR, "cube_data_config_extra_cols.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_config_extra_cols.csv")
    cube, errors = cli_build(
        config=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=False,
        validation_errors_file_out=Path(output, "validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(errors, list)
    output_path = Path(output, "validation_errors.json").resolve()
    assert output_path.exists()


if __name__ == "__main__":
    pytest.main()
