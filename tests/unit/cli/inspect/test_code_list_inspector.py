from csvcubed.models.sparqlresults import CodeListTableIdentifers
from csvcubed.utils.sparql_handler.code_list_state import CodeListState
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

    code_list_inspector = CodeListState(rdf_manager.csvw_state)
    code_list_identifiers = code_list_inspector._code_list_table_identifiers

    assert len(code_list_identifiers) == 1
    assert code_list_identifiers[0] == CodeListTableIdentifers(
        csv_url="some-dimension.csv", concept_scheme_url="some-dimension.csv#code-list"
    )
    # it should have one value returned
