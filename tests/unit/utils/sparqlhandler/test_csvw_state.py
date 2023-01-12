from csvcubed.utils.sparql_handler.csvw_state import CsvWState
from csvcubed.utils.tableschema import CsvwRdfManager
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_get_primary_catalog_metadata():
    """
    1 [X]) Starting from 'the_thing':
        the CsvWState object calls the function which retrives the catalog metadata from the primary graph.

    2 [X]) In the object, we call the cached property to get the catalog meta data result[s]

    3 [X]) In the cached property, select_csvw_catalog_metadata obtains the results from the sparql query.
        This should be a list of resultrow objects.
        Then we call the map function providing it with this list.

    4 [X]) In the map function, we want to:
        a) Iterate over each of the resultrow objects (performing an as_dict per result)
        b) Create a catalogmetadataresult object containing the metadata properties for each resultrow objects
        b) Add this catalogmetadataresult to a list and return this list

    5 [X]) This should mean that 'results' in the cached property is a list of catalogmetadataresults

    6 []) Using the primary_graph_uri, access the catalogmetadataresult in the 'results' list for the return value of the API function
        (AKA - what this test is calling)
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_state = CsvWState(csvw_rdf_manager.rdf_graph, csvw_metadata_json_path)

    the_thing = csvw_state.get_primary_catalog_metadata()

    # assert the_thing.graph_uri == "file:///workspaces/csvcubed/tests/test-cases/cli/inspect/pivoted-single-measure-dataset/qb-id-10004.csv-metadata.json"
    assert the_thing.graph_uri == "file:///" + str(csvw_metadata_json_path)[1:]
    # change this(^) to use premoveprefix

    # sparql_results = {
    #     "graph": { "type": "uri" , "value": "file:///workspaces/csvcubed/tests/test-cases/cli/inspect/pivoted-single-measure-dataset/qb-id-10004.csv-metadata.json" } ,
    #     "dataset": { "type": "uri" , "value": "file:///Users/charlesrendle/git/csvcubed/csvcubed/qb-id-10004.csv#dataset" } ,
    #     "title": { "type": "literal" , "xml:lang": "en" , "value": "Pivoted Shape Cube" } ,
    #     "label": { "type": "literal" , "xml:lang": "en" , "value": "Pivoted Shape Cube" } ,
    #     "issued": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#dateTime" , "value": "2022-10-28T13:35:50.699296" } ,
    #     "modified": { "type": "literal" , "datatype": "http://www.w3.org/2001/XMLSchema#dateTime" , "value": "2022-10-28T13:35:50.699296" } ,
    #     "identifier": { "type": "literal" , "value": "qb-id-10004" }
    #   }

    # expected = (
    #     dataset_uri='qb-id-10004.csv#dataset',
    #     graph_uri='file:///workspaces/csvcubed/tests/test-cases/c...s=[''],
    #     themes=[''],
    #     keywords=[''],
    #     contact_point='None',
    #     identifier='qb-id-10004',
    #     comment='None',
    #     description='None'
    # )
