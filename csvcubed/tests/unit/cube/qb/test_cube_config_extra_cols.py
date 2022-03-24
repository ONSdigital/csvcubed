from enum import Enum
from pathlib import Path

import pytest
from csvcubed.cli.build import build as cli_build
from csvcubed.models.cube import Cube
from csvcubed.readers.cubeconfig import v1_0
from csvcubed.readers.cubeconfig import schema_versions
from tests.unit.test_baseunit import get_test_cases_dir

TEST_CASE_DIR = Path(get_test_cases_dir().absolute(), "config")


@pytest.fixture(autouse=True)
def set_testing_v1_schema_url():
    """
    Configure the tests to believe that the locally defined cube-config-schema.json is the correct V1 schema.
    """

    schema_versions.QubeConfigJsonSchemaVersion.DEFAULT_V1_SCHEMA_URL = (
        "../csvcubed/schema/cube-config-schema.json"
    )


def test_build_with_fail():
    config = Path(TEST_CASE_DIR, "cube_data_config_extra_cols.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_config_extra_cols.csv")
    with pytest.raises(SystemExit):
        cli_build(
            config_path=config,
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
        config_path=config,
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
