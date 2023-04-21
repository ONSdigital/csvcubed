from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from csvcubeddevtools.helpers.file import get_test_cases_dir

from csvcubed.cli.pullcsvw.pull import HttpCsvWPuller, pull

_test_cases_dir = get_test_cases_dir()


@pytest.mark.vcr
def test_extracting_dependant_urls():
    csvw_puller = HttpCsvWPuller(
        "https://w3c.github.io/csvw/tests/test015/csv-metadata.json"
    )
    dependencies = csvw_puller._get_csvw_dependencies_follow_relative_only()
    assert dependencies == {"https://w3c.github.io/csvw/tests/test015/tree-ops.csv"}


@pytest.mark.vcr
def test_extracting_relative_base_url_from_context():
    csvw_puller = HttpCsvWPuller(
        "https://w3c.github.io/csvw/tests/test273-metadata.json"
    )
    dependencies = csvw_puller._get_csvw_dependencies_follow_relative_only()

    assert dependencies == {"https://w3c.github.io/csvw/tests/test273/action.csv"}


@pytest.mark.vcr
def test_extracting_multiple_tables_with_url_schemas():
    csvw_puller = HttpCsvWPuller(
        "https://w3c.github.io/csvw/tests/test034/csv-metadata.json"
    )
    dependencies = csvw_puller._get_csvw_dependencies_follow_relative_only()

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
    csvw_puller = HttpCsvWPuller(f"{base}/csv-metadata.json")
    dependencies = csvw_puller._get_csvw_dependencies_follow_relative_only()

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
    base = (
        "https://raw.githubusercontent.com/GSS-Cogs/csvcubed-demo/main/sweden_at_eurovision_no_missing/"
        "convention_out"
    )
    csvw_puller = HttpCsvWPuller(
        f"{base}/sweden-at-eurovision-no-missing.csv-metadata.json"
    )
    dependencies = csvw_puller._get_csvw_dependencies_follow_relative_only()

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
    csvw_puller = HttpCsvWPuller(f"{base}/transitive.csv-metadata.json")
    dependencies = csvw_puller._get_csvw_dependencies_follow_relative_only()

    assert dependencies == {
        f"{base}/data.csv",
        f"{base}/dimension.table.json",
        f"{base}/dimension.csv",
        f"{base}/transitive.1.json",
        f"{base}/transitive.2.json",
    }


@pytest.mark.vcr
def test_pull_with_absolute_dependency():
    """
    Test that absolute (non-relative) dependencies of CSV-Ws can also be successfully pulled.
    """
    with TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        pull(
            "https://raw.githubusercontent.com/GSS-Cogs/reusable-rdf-resources/main/rdf-definitions/attributes/"
            "analyst-function-obs-marker.csv-metadata.json",
            tmp,
        )
        assert (tmp / "analyst-function-obs-marker.csv-metadata.json").exists()
        """
            Note that since the CSV file in this example is at an absolute non-relative URL on a different domain,
            we don't download it.

            If we did download it, we'd have to fundamentally rewrite the CSV-W metadata.json document to make it point
            to it.
        """


@pytest.mark.vcr
def test_relative_base_url():
    """
    Test that a relative `@base` URL can successfully be used with the pull command.
    """
    csvw_doc = (
        _test_cases_dir
        / "pull"
        / "relative-base-url"
        / "sweden-at-eurovision-complete-dataset.csv-metadata.json"
    )
    with TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        pull(str(csvw_doc), tmp)

        assert (
            tmp / "sweden-at-eurovision-complete-dataset.csv-metadata.json"
        ).exists()
        contents_dir = tmp / "contents"
        assert contents_dir.exists()

        # Test the CSV-W dependencies.
        assert (contents_dir / "entrant.csv").exists()
        assert (contents_dir / "entrant.table.json").exists()
        assert (contents_dir / "language.csv").exists()
        assert (contents_dir / "language.table.json").exists()
        assert (contents_dir / "song.csv").exists()
        assert (contents_dir / "song.table.json").exists()
        assert (contents_dir / "sweden-at-eurovision-complete-dataset.csv").exists()
        assert (contents_dir / "year.csv").exists()
        assert (contents_dir / "year.table.json").exists()

        # Test the RDF dependencies
        assert (contents_dir / "entrant.csv-metadata.json").exists()
        assert (contents_dir / "language.csv-metadata.json").exists()
        assert (contents_dir / "song.csv-metadata.json").exists()
        assert (contents_dir / "year.csv-metadata.json").exists()


if __name__ == "__main__":
    pytest.main()
