from pathlib import Path
from csvcubeddevtools.helpers.file import get_test_cases_dir

# import the generate_maximaly_complex_scvfile function the create a csv file after that wun the build command in a temp directory(feed that directory to the inpect command bellow) then the inspect command will function.


@profile
def main(csvw_path: Path):
    from csvcubed.cli.inspect.inspect import inspect

    inspect(csvw_path)


test_cases_dir = get_test_cases_dir() / "profiling"

maximally_complex_csvw_path = (
    test_cases_dir / "max-csvw" / "stress-test-data-set.csv-metadata.json"
)

main(maximally_complex_csvw_path)
