import pytest
from csvcubeddevtools.helpers.file import get_test_cases_dir

from csvcubed.cli.pullcsvw.pull import _get_csvw_dependencies

_test_cases_dir = get_test_cases_dir()


@pytest.mark.vcr
def test_extracting_dependant_urls():
    dependencies = _get_csvw_dependencies(
        "https://w3c.github.io/csvw/tests/test015/csv-metadata.json"
    )

    assert dependencies == {"https://w3c.github.io/csvw/tests/test015/tree-ops.csv"}


@pytest.mark.vcr
def test_extracting_relative_base_url_from_context():
    dependencies = _get_csvw_dependencies(
        "https://w3c.github.io/csvw/tests/test273-metadata.json"
    )

    assert dependencies == {"https://w3c.github.io/csvw/tests/test273/action.csv"}


@pytest.mark.vcr
def test_extracting_multiple_tables_with_url_schemas():
    dependencies = _get_csvw_dependencies(
        "https://w3c.github.io/csvw/tests/test034/csv-metadata.json"
    )

    assert dependencies == {
        "https://w3c.github.io/csvw/tests/test034/gov.uk/data/professions.csv",
        "https://w3c.github.io/csvw/tests/test034/gov.uk/schema/professions.json",
        "https://w3c.github.io/csvw/tests/test034/gov.uk/data/organizations.csv",
        "https://w3c.github.io/csvw/tests/test034/gov.uk/schema/organizations.json",
        "https://w3c.github.io/csvw/tests/test034/senior-roles.csv",
        "https://w3c.github.io/csvw/tests/test034/gov.uk/schema/senior-roles.json",
        "https://w3c.github.io/csvw/tests/test034/junior-roles.csv",
        "https://w3c.github.io/csvw/tests/test034/gov.uk/schema/junior-roles.json",
    }


@pytest.mark.vcr
def test_get_relative_dependencies():
    base = "https://w3c.github.io/csvw/tests/test034"
    dependencies = _get_csvw_dependencies(f"{base}/csv-metadata.json")

    assert dependencies == {
        f"{base}/gov.uk/data/professions.csv",
        f"{base}/gov.uk/schema/professions.json",
        f"{base}/gov.uk/data/organizations.csv",
        f"{base}/gov.uk/schema/organizations.json",
        f"{base}/senior-roles.csv",
        f"{base}/gov.uk/schema/senior-roles.json",
        f"{base}/junior-roles.csv",
        f"{base}/gov.uk/schema/junior-roles.json",
    }


@pytest.mark.vcr
def test_get_tableschema_dependencies():
    base = "https://raw.githubusercontent.com/GSS-Cogs/csvcubed-demo/main/sweden_at_eurovision_no_missing/convention_out"
    dependencies = _get_csvw_dependencies(
        f"{base}/sweden-at-eurovision-no-missing.csv-metadata.json"
    )

    assert dependencies == {
        f"{base}/entrant.csv",
        f"{base}/entrant.table.json",
        f"{base}/entrant.csv-metadata.json",
        f"{base}/language.csv",
        f"{base}/language.table.json",
        f"{base}/language.csv-metadata.json",
        f"{base}/song.csv",
        f"{base}/song.table.json",
        f"{base}/song.csv-metadata.json",
        f"{base}/year.csv",
        f"{base}/year.table.json",
        f"{base}/year.csv-metadata.json",
        f"{base}/sweden-at-eurovision-no-missing.csv",
    }


@pytest.mark.vcr
def test_extracting_rdf_dependency():
    """
    Test we can successfully extract RDF-defined file dependencies (and so pull the files too!)
    """
    base = (
        "https://raw.githubusercontent.com/GSS-Cogs/csvcubed/dc1b8df2cd306346e17778cb951417935c91e78b/tests/"
        "test-cases/cli/inspect/dependencies"
    )

    dependencies = _get_csvw_dependencies(f"{base}/transitive.csv-metadata.json")

    assert dependencies == {
        f"{base}/data.csv",
        f"{base}/dimension.table.json",
        f"{base}/dimension.csv",
        f"{base}/transitive.1.json",
        f"{base}/transitive.2.json",
    }


if __name__ == "__main__":
    pytest.main()
