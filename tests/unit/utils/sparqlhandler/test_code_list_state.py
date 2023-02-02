from csvcubed.utils.sparql_handler.code_list_state import CodeListState
from csvcubed.utils.tableschema import CsvwRdfManager
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_first_code_list_inspector_function():
    """
    ToDO: ADD DESC
    """
    some_path = _test_case_base_dir / "clearance-origin.csv-metadata.json"

    csvw_rdf_manager = CsvwRdfManager(some_path)
    code_list_state = CodeListState(csvw_rdf_manager.csvw_state)

    something = code_list_state._code_list_table_identifiers()

    assert something.csv_url == "clearance-origin.csv"


def test_edited_query():
    """ """
    some_path = _test_case_base_dir / "clearance-origin.csv-metadata.json"

    csvw_rdf_manager = CsvwRdfManager(some_path)
    code_list_state = CodeListState(csvw_rdf_manager.csvw_state)

    something = code_list_state.link_csv_url_to_concept_scheme_url()

    assert something[1] == "concept-sceheme"
