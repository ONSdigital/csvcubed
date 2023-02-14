from pathlib import Path

import pytest

from csvcubed.readers.skoscodelistreader import extract_code_list_concept_scheme_info
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir()
_skos_codelist_reader_test_cases = (
    _test_case_base_dir / "readers" / "skoscodelistreader"
)


def test_skos_concept_schema_csvw_with_multiple_tables():
    """
    Ensure that we can successfully extract the concept scheme URI and concept URI template from a roughly standard codelist CSV-W with multiple tables.
    """
    code_list_csvw = (
        _test_case_base_dir / "utils" / "csvw" / "industry-grouping.csv-metadata.json"
    )
    csv_path, cs_uri, concept_uri_template = extract_code_list_concept_scheme_info(
        code_list_csvw
    )

    assert csv_path == "industry-grouping.csv"
    assert (
        cs_uri
        == "http://gss-data.org.uk/data/gss_data/trade/ons-international-trade-in-services-by-subnational-areas-of-the-uk#scheme/industry-grouping"
    )
    assert (
        concept_uri_template
        == "http://gss-data.org.uk/data/gss_data/trade/ons-international-trade-in-services-by-subnational-areas-of-the-uk#concept/industry-grouping/{+notation}"
    )


def test_skos_concept_scheme_csvw():
    """
    Ensure that we can successfully extract the concept scheme URI and concept URI template from a roughly standard codelist CSV-W.
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


def test_num_of_variables_in_about_url_invalid_exception():
    """
    Ensures that an exception is thrown when the number of variables in about url are invalid.
    """
    code_list_csvw = (
        _skos_codelist_reader_test_cases
        / "about-url-invalid-variable.csv-metadata.json"
    )

    with pytest.raises(ValueError) as ex:
        extract_code_list_concept_scheme_info(code_list_csvw)

    assert (
        "Unexpected number of variables in aboutUrl Template. Expected 1, found 2"
        in str(ex)
    )


def test_legacy_composite_code_list():
    """Test that a legacy composite code list returns a sensible `about-url-wriUrl`. Addresses bug in issue #389."""
    location_test_case: Path = (
        _skos_codelist_reader_test_cases / "location.csv-metadata.json"
    )
    (_, _, concept_uri_template) = extract_code_list_concept_scheme_info(
        location_test_case
    )

    # aboutUrl is actually `{+uri}` inside the CSV-W, but is standardised to `{+notation}`.
    assert concept_uri_template == "{+notation}"


if __name__ == "__main__":
    pytest.main()
