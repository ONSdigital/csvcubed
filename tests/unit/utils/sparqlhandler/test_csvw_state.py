from csvcubed.utils.sparql_handler.csvw_state import CsvWState
from csvcubed.utils.tableschema import CsvwRdfManager
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"

def test_get_primary_catalog_metadata():
    """
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_state = CsvWState(csvw_rdf_manager.rdf_graph, csvw_metadata_json_path)

    the_thing = csvw_state.get_primary_catalog_metadata()

    assert the_thing == ""