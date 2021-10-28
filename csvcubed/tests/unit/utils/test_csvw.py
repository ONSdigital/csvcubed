import pytest

from tests.unit.test_baseunit import get_test_cases_dir
from csvcubed.utils.csvw import get_dependent_local_files, get_first_table_schema

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


def test_get_first_table_group_schema_relative_path():
    """
    Test fetching the first table group schema where the tableSchema is defined with a relative path.
    """
    csv_url, first_table_schema = get_first_table_schema(
        csvw_utils_test_cases / "code-list.csv-metadata.json"
    )
    assert csv_url == "code-list.csv"
    assert first_table_schema is not None
    assert first_table_schema["columns"][0]["titles"] == "Label"


def test_get_first_table_group_schema_relative_path_multiple_tables():
    """
    Test fetching the first table group schema where the tableSchema is defined with a relative path.
    """
    csv_url, first_table_schema = get_first_table_schema(
        csvw_utils_test_cases / "code-list-multiple-tables.csv-metadata.json"
    )

    assert csv_url == "code-list.csv"
    assert first_table_schema is not None
    assert first_table_schema["columns"][0]["titles"] == "Label"


def test_get_first_table_group_schema_uri_multiple_tables():
    """
    Test fetching the first table group schema where the tableSchema is defined with an absolute URI.
    """
    csv_url, first_table_schema = get_first_table_schema(
        csvw_utils_test_cases / "code-list-multiple-tables-uri.csv-metadata.json"
    )

    assert csv_url == "code-list.csv"
    assert first_table_schema is not None
    assert first_table_schema["columns"][0]["titles"] == "Label"


def test_get_first_table_group_schema_relative_uri_multiple_tables():
    """
    Test fetching the first table group schema where the tableSchema is defined with a URI relative to the base.
    """
    csv_url, first_table_schema = get_first_table_schema(
        csvw_utils_test_cases
        / "code-list-multiple-tables-relative-uri.csv-metadata.json"
    )

    assert csv_url == "code-list.csv"
    assert first_table_schema is not None
    assert first_table_schema["columns"][0]["titles"] == "Label"


if __name__ == "__main__":
    pytest.main()
