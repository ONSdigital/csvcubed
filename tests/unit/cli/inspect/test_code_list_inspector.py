import pytest

from csvcubed.models.sparqlresults import CatalogMetadataResult, CodeListTableIdentifers
from tests.helpers.inspectors_cache import get_code_list_inspector, get_csvw_rdf_manager
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_code_list_table_identifiers():
    """The test checks for the codelist idetifiers and returns the table identifier thats
    property_url contains the skos:inScheme."""

    path_to_cube = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(path_to_cube)
    code_list_identifiers = code_list_inspector._code_list_table_identifiers

    assert len(code_list_identifiers) == 1
    assert code_list_identifiers[0] == CodeListTableIdentifers(
        csv_url="some-dimension.csv", concept_scheme_url="some-dimension.csv#code-list"
    )


def test_code_list_table_identifiers_error():
    """the test checks when multiple table identifiers property_url contains the
    skos:inScheme a KeyError is thrown with the correct error message."""

    path_to_cube = (
        _test_case_base_dir / "itis-industry-multiple-skos-inscheme.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(path_to_cube)

    with pytest.raises(KeyError) as exception:
        _ = code_list_inspector._code_list_table_identifiers

    assert (
        "Found multiple skos:inScheme columns in 'itis-industry-multiple-skos-inscheme.csv'."
    ) in str(exception.value)


def test_get_catalog_metadata_for_concept_scheme():
    """This test ensures when the get_catalog_metadata_for_concept_scheme() check passes and returns
    the CatalogMetadataResult the objects dataset_uri does match with the expected concept_scheme_url."""

    path_to_cube = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(path_to_cube)

    the_result = code_list_inspector.get_catalog_metadata_for_concept_scheme(
        "some-dimension.csv#code-list"
    )

    assert isinstance(the_result, CatalogMetadataResult)
    assert the_result.dataset_uri == "some-dimension.csv#code-list"


def test_get_catalog_metadata_for_concept_scheme_error():
    """This test ensures when the get_catalog_metadata_for_concept_scheme() check fails(concept_scheme_url
    doesn't match) the relevant ValueError is thrown with the correct error message."""

    path_to_cube = (
        _test_case_base_dir / "itis-industry-no-skos-inscheme.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(path_to_cube)

    with pytest.raises(KeyError) as exception:
        _ = code_list_inspector.get_catalog_metadata_for_concept_scheme(
            "http://gss-data.org.uk/data/gss_data/trade/ons-international-trade-in-services#scheme/it-industry"
        )

    assert (
        "Can not find Catalogue Meatadata associated with the concept scheme URL 'http://gss-data.org.uk/data/gss_data/trade/ons-international-trade-in-services#scheme/it-industry'"
    ) in str(exception.value)


def test_get_table_identifiers_for_concept_scheme_error():
    """This functions ensures when the given concept_scheme_url doent mach any of the
    CodeListTableIdentifiers concept_scheme_url KeyError is thrown with the correct rror message."""

    path_to_cube = (
        _test_case_base_dir / "itis-industry-no-skos-inscheme.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(path_to_cube)

    concept_scheme_url = "http://gss-data.org.uk/data/gss_data/trade/ons-international-trade-in-services#scheme/itis-industry"

    with pytest.raises(KeyError) as exception:
        _ = code_list_inspector.get_table_identifiers_for_concept_scheme(
            concept_scheme_url
        )
    assert (
        "Could not find code list table identifiers for ConceptScheme URL: 'http://gss-data.org.uk/data/gss_data/trade/ons-international-trade-in-services#scheme/itis-industry'"
    ) in str(exception.value)


def test_dereference_code_list_uri_to_label():
    """"""
    path_to_cube = (
        _test_case_base_dir
        / "code-list-with-uri-identifier-as-identifier/category.csv-metadata.json"
    )
    code_list_inspector = get_code_list_inspector(path_to_cube)

    concept_scheme_uri = "category.csv#code-list"

    result = code_list_inspector.dereference_code_list_uri_to_label(concept_scheme_uri)

    assert len(result) == 3
    assert (
        result["boosting-productivity-pay-jobs-and-living-standards"]
        == "Boosting productivity, pay, jobs and living standards by growing the private sector"
    )
