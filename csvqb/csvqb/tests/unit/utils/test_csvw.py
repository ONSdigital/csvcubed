import pytest

from csvqb.tests.unit.test_baseunit import get_test_cases_dir
from csvqb.utils.csvw import get_dependent_local_files

csvw_utils_test_cases = get_test_cases_dir() / "utils" / "csvw"


def test_extracting_dependent_files():
    csvw_file = csvw_utils_test_cases / "multiple_tables.csv-metadata.json"
    assert csvw_file.exists()

    dependent_files = get_dependent_local_files(csvw_file)

    # test extracting the base path from the `@context`
    expected_base_path = csvw_file.parent / "some-base-path"
    for file in dependent_files:
        assert file.parent == expected_base_path

    dependent_file_names = {f.name for f in dependent_files}

    assert dependent_file_names == {
        "data-file.csv",
        "another-data-file.csv",
        "table-schema.json",
        "another-table-schema.json",
    }


def test_no_dependent_local_files_when_base_is_uri():
    """ """
    csvw_file = csvw_utils_test_cases / "uri_base.csv-metadata.json"
    assert csvw_file.exists()

    dependent_files = get_dependent_local_files(csvw_file)
    assert len(dependent_files) == 0


if __name__ == "__main__":
    pytest.main()
