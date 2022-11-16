from tempfile import TemporaryDirectory
from pathlib import Path

from csvcubeddevtools.helpers.file import get_test_cases_dir
from tests.stress.buildpreprocess import generate_maximally_complex_csv

def main(csv_path: Path, qube_config_json_path: Path, tmp_dir: Path):
    from csvcubed.cli.build import build

    build(
        csv_path=csv_path,
        output_directory=tmp_dir,
        config_path=qube_config_json_path,
        fail_when_validation_error_occurs=True,
        validation_errors_file_name=None,
    )

test_cases_dir = get_test_cases_dir() / "profiling"
qube_config_json_path = test_cases_dir / "config.json"

with TemporaryDirectory() as tmp:
    tmp_dir = Path(tmp)
    generate_maximally_complex_csv(1000, tmp_dir)
    csv_path = tmp_dir / "stress.csv"

    main(csv_path, qube_config_json_path, tmp_dir)