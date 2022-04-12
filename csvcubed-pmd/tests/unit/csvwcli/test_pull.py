import pytest
from csvcubeddevtools.helpers.file import get_test_cases_dir

from csvcubedpmd.csvwcli.pull import (
    _get_csvw_dependencies_absolute,
    _get_csvw_dependencies_relative,
)


_test_cases_dir = get_test_cases_dir()


@pytest.mark.vcr
def test_extracting_dependant_urls():
    dependencies = _get_csvw_dependencies_absolute(
        "https://w3c.github.io/csvw/tests/test015/csv-metadata.json"
    )

    assert dependencies == {"https://w3c.github.io/csvw/tests/test015/tree-ops.csv"}


@pytest.mark.vcr
def test_extracting_relative_base_url_from_context():
    dependencies = _get_csvw_dependencies_absolute(
        "https://w3c.github.io/csvw/tests/test273-metadata.json"
    )

    assert dependencies == {"https://w3c.github.io/csvw/tests/test273/action.csv"}

    dependencies = _get_csvw_dependencies_relative(
        "https://w3c.github.io/csvw/tests/test273-metadata.json"
    )

    assert dependencies == {"test273/action.csv"}


@pytest.mark.vcr
def test_extracting_multiple_tables_with_url_schemas():
    dependencies = _get_csvw_dependencies_absolute(
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
    dependencies = _get_csvw_dependencies_relative(
        "https://w3c.github.io/csvw/tests/test034/csv-metadata.json"
    )

    assert dependencies == {
        "gov.uk/data/professions.csv",
        "gov.uk/schema/professions.json",
        "gov.uk/data/organizations.csv",
        "gov.uk/schema/organizations.json",
        "senior-roles.csv",
        "gov.uk/schema/senior-roles.json",
        "junior-roles.csv",
        "gov.uk/schema/junior-roles.json",
    }


@pytest.mark.vcr
def test_get_relative_dependencies_excludes_absolute_dependencies():
    dependencies = _get_csvw_dependencies_relative(
        _test_cases_dir / "absolute.csv-metadata.json"
    )

    assert len(dependencies) == 0


@pytest.mark.vcr
def test_get_tableschema_dependencies():
    dependencies = _get_csvw_dependencies_relative(
        "https://ci.ukstats.dev/job/GSS_data/job/Trade/job/csvcubed/job/HMRC-alcohol-bulletin/job/HMRC-alcohol-bulletin/lastSuccessfulBuild/artifact/outputs/alcohol-sub-type.csv-metadata.json"
    )

    assert dependencies == {"alcohol-sub-type.csv", "alcohol-sub-type.table.json"}


if __name__ == "__main__":
    pytest.main()
