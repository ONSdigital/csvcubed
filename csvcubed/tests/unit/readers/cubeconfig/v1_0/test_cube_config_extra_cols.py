from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from csvcubed.cli.build import build as cli_build
from csvcubed.models.cube import Cube
from tests.unit.test_baseunit import get_test_cases_dir

TEST_CASE_DIR = get_test_cases_dir().absolute() / "readers" / "cube-config" / "v1.0"


@pytest.mark.vcr
def test_build_with_fail():
    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        config = Path(TEST_CASE_DIR, "cube_data_config_extra_cols.json")
        output = temp_dir / "out"
        csv = Path(TEST_CASE_DIR, "cube_data_config_extra_cols.csv")
        with pytest.raises(SystemExit):
            cli_build(
                config_path=config,
                output_directory=output,
                csv_path=csv,
                fail_when_validation_error_occurs=True,
                validation_errors_file_out=Path(output, "validation_errors.json"),
            )


@pytest.mark.vcr
def test_build_without_fail():
    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        config = Path(TEST_CASE_DIR, "cube_data_config_ok.json")
        output = temp_dir / "out"
        csv = Path(TEST_CASE_DIR, "cube_data_config_ok.csv")
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
