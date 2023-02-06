import pytest

from csvcubed.models.sparqlresults import CatalogMetadataResult, CodeListTableIdentifers
from csvcubed.utils.sparql_handler.code_list_inspector import CodeListInspector
from csvcubed.utils.tableschema import CsvwRdfManager
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = (
    get_test_cases_dir() / "cli" / "inspect" / "pivoted-multi-measure-dataset"
)


def test_code_list_table_identifiers():
    """the test checks for the codelist idetifiers are available but
    in the mean time the cube doesn't have a record in the codelist identifiers"""

    path_to_cube = _test_case_base_dir / "qb-id-10003.csv-metadata.json"

    rdf_manager = CsvwRdfManager(path_to_cube)

    code_list_inspector = CodeListInspector(rdf_manager.csvw_state)
    code_list_identifiers = code_list_inspector._code_list_table_identifiers

    assert len(code_list_identifiers) == 1
    assert code_list_identifiers[0] == CodeListTableIdentifers(
        csv_url="some-dimension.csv", concept_scheme_url="some-dimension.csv#code-list"
    )
    # it should have one value returned


# make a fail test for the one above
def test_code_list_table_identifiers_error():
    """the test checks for the codelist idetifiers are available but
    in the mean time the cube doesn't have a record in the codelist identifiers"""

    path_to_cube = (
        get_test_cases_dir()
        / "cli"
        / "inspect"
        / "itis-industry-multiple-skos-inscheme.csv-metadata.json"
    )

    rdf_manager = CsvwRdfManager(path_to_cube)

    code_list_inspector = CodeListInspector(rdf_manager.csvw_state)

    with pytest.raises(KeyError) as exception:
        _ = code_list_inspector._code_list_table_identifiers

    assert (
        "Found multiple skos:inScheme columns in 'itis-industry-multiple-skos-inscheme.csv'."
    ) in str(exception.value)


def test_get_csvw_catalog_metadata():

    path_to_cube = _test_case_base_dir / "qb-id-10003.csv-metadata.json"

    rdf_manager = CsvwRdfManager(path_to_cube)

    code_list_inspector = CodeListInspector(rdf_manager.csvw_state)

    the_result = code_list_inspector.get_csvw_catalog_metadata()

    assert isinstance(the_result, CatalogMetadataResult)
    assert the_result.dataset_uri == "some-dimension.csv#code-list"


# make a fail test for the one above


# test for keyerror for the get_table_identifiers_for_concept_scheme
