from tempfile import TemporaryDirectory
from pathlib import Path

from csvcubeddevtools.helpers.file import get_test_cases_dir

_test_cases_dir = get_test_cases_dir() / "profiling"

_csv_path = _test_cases_dir / "data.csv"
_qube_config_json_path = _test_cases_dir / "config.json"

with TemporaryDirectory() as tmp:
    tmp_dir = Path(tmp)

    from csvcubed.cli.build import build

    build(
        csv_path=_csv_path,
        output_directory=tmp_dir,
        config_path=_qube_config_json_path,
        fail_when_validation_error_occurs=True,
        validation_errors_file_name=None,
    )
