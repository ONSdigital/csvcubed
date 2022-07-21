from pathlib import Path
import pandas as pd
import pytest

from csvcubed.readers.skoscodelistreader import (
    extract_code_list_concept_scheme_info,
)
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.cube.qb import CatalogMetadata
from csvcubed.models.cube import Cube, NewQbUnit, NewQbMeasure
from csvcubed.models.cube.qb.components import (
    NewQbDimension,
    NewQbCodeListInCsvW,
    QbSingleMeasureObservationValue,
)

from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir()
_csvw_test_cases_dir = get_test_cases_dir() / "utils" / "csvw"
_skos_codelist_reader_test_cases = (
    _test_case_base_dir / "readers" / "skoscodelistreader"
)


def test_skos_concept_scheme_csvw():
    """
    Ensure that we can successfully extract the concept scheme URI and concept URI template from a roughly standard
     codelist CSV-W.
    """
    code_list_csvw = (
        _test_case_base_dir / "utils" / "csvw" / "code-list.csv-metadata.json"
    )
    csv_path, cs_uri, concept_uri_template = extract_code_list_concept_scheme_info(
        code_list_csvw
    )

    assert csv_path == "code-list.csv"
    assert cs_uri == "http://gss-data.org.uk/def/trade/concept-scheme/age-of-business"
    assert (
        concept_uri_template
        == "http://gss-data.org.uk/def/trade/concept/age-of-business/{+notation}"
    )


def test_skos_in_scheme_missing():
    """
    Ensure that we get an appropriate exception when the `skos:inScheme` triple column is missing.
    """
    code_list_csvw = (
        _skos_codelist_reader_test_cases / "skos-in-scheme-missing.csv-metadata.json"
    )

    with pytest.raises(ValueError) as ex:
        extract_code_list_concept_scheme_info(code_list_csvw)

    assert "is missing `skos:inScheme` column" in str(ex)


def test_about_url_missing():
    """
    Ensure that we get an appropriate exception when the concept aboutUrl is missing.
    """
    code_list_csvw = (
        _skos_codelist_reader_test_cases / "about-url-missing.csv-metadata.json"
    )

    with pytest.raises(ValueError) as ex:
        extract_code_list_concept_scheme_info(code_list_csvw)

    assert "is missing `aboutUrl` property" in str(ex)


def test_csv_url_missing():
    """
    Ensure that we get an appropriate exception when the table's URL is missing.
    """
    code_list_csvw = (
        _skos_codelist_reader_test_cases / "csv-url-missing.csv-metadata.json"
    )

    with pytest.raises(ValueError) as ex:
        extract_code_list_concept_scheme_info(code_list_csvw)

    assert "is missing `url` property for code list table" in str(ex)


def test_legacy_composite_code_list():
    """Test that a legacy composite code list returns a sensible `aboutUrl`. Addresses bug in issue #389."""
    location_test_case: Path = (
        _skos_codelist_reader_test_cases / "location.csv-metadata.json"
    )
    (_, _, concept_uri_template) = extract_code_list_concept_scheme_info(
        location_test_case
    )

    # aboutUrl is actually `{+uri}` inside the CSV-W, but is standardised to `{+notation}`.
    assert concept_uri_template == "{+notation}"


def test_temp():
    """
    TODO Add Intro
    """
    table_schema_dependencies_dir = _csvw_test_cases_dir / "table-schema-dependencies"
    csvw_metadata_json_path = (
        table_schema_dependencies_dir
        / "sectors-economic-estimates-2018-trade-in-services.csv-metadata.json"
    )

    data = pd.DataFrame(
        {
            "Industry Grouping": [
                "http://data.europa.eu/nuts/code/UKC",
                "http://data.europa.eu/nuts/code/UKL",
                "http://data.europa.eu/nuts/code/UKD",
            ],
            "Observed Value": [1, 2, 3],
        }
    )

    metadata = CatalogMetadata("Some Dataset")
    columns = [
        QbColumn(
            "Industry Grouping",
            NewQbDimension(
                "Industry Grouping",
                code_list=NewQbCodeListInCsvW(csvw_metadata_json_path),
            ),
        ),
        QbColumn(
            "Observed Value",
            QbSingleMeasureObservationValue(
                unit=NewQbUnit("Num of students"), measure=NewQbMeasure("Total")
            ),
        ),
    ]

    cube = Cube(metadata, data, columns)
    assert cube is not None


if __name__ == "__main__":
    pytest.main()
