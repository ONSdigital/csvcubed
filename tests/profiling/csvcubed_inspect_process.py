from pathlib import Path
from tempfile import TemporaryDirectory
from csvcubeddevtools.helpers.file import get_test_cases_dir
from csvcubed.cli.build import build
from memory_profiler import profile

from tests.stress.buildpreprocess import generate_maximally_complex_csv

# import the generate_maximaly_complex_scvfile function the create a csv file after that wun the build command in a temp directory(feed that directory to the inpect command bellow) then the inspect command will function.


@profile(precision=4)
def main(csvw_path: Path):
    from csvcubed.cli.inspect.inspect import inspect

    inspect(csvw_path)


with TemporaryDirectory() as tmp:
    tmp_dir = Path(tmp)
    generate_maximally_complex_csv(1000, tmp_dir)
    csv_path = tmp_dir / "stress.csv"

    test_cases_dir = get_test_cases_dir() / "profiling"
    qube_config_json_path = test_cases_dir / "config.json"

    build(
        csv_path=csv_path,
        output_directory=tmp_dir,
        config_path=qube_config_json_path,
        fail_when_validation_error_occurs=True,
        validation_errors_file_name=None,
    )
    maximally_complex_csvw_path = tmp_dir / "stress-test-data-set.csv-metadata.json"

    main(maximally_complex_csvw_path)
