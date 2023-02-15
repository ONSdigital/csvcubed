from csvcubed.models.csvwtype import CSVWType
from csvcubed.utils.sparql_handler.csvw_inspector import CsvWInspector
from csvcubed.utils.sparql_handler.sparql import path_to_file_uri_for_rdflib
from csvcubed.utils.tableschema import CsvwRdfManager
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_get_primary_catalog_metadata():
    """
    Tests that primary catalog metadata can correctly be retrieved from an input
    csvw metadata json file's CsvwRdfManager object, by accessing its csvw_inspector and
    running the function.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    primary_graph_identifier = path_to_file_uri_for_rdflib(csvw_metadata_json_path)

    test_catalog_metadata_result = (
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
    )

    assert test_catalog_metadata_result.graph_uri == primary_graph_identifier


def test_detect_csvw_type_qb_dataset():
    """
    Tests the detection of the csvw_type of an input metadata json file that has a CsvwRdfManager
    object created from it, in this case to correctly detect a QbDataset csvw type from its csvw_inspector.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)

    csvw_type = csvw_rdf_manager.csvw_inspector.csvw_type
    assert csvw_type == CSVWType.QbDataSet


def test_detect_csvw_type_code_list():
    """
    Tests the detection of the csvw_type of an input metadata json file that has a CsvwRdfManager
    object created from it, in this case to correctly detect a CodeList csvw type from its csvw_inspector.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "some-dimension.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)

    csvw_type = csvw_rdf_manager.csvw_inspector.csvw_type
    assert csvw_type == CSVWType.CodeList


def test_get_table_schema_properties():
    """
    Ensures that the correct table schema properties are returned for the given code list.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "some-dimension.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)

    csvw_inspector: CsvWInspector = CsvWInspector(
        csvw_rdf_manager.rdf_graph, csvw_metadata_json_path
    )

    result = csvw_inspector.get_table_schema_properties()

    assert (
        result.table_schema_properties[0].about_url
        == "some-dimension.csv#{+uri_identifier}"
    )
    assert result.table_schema_properties[0].table_url == "some-dimension.csv"
    assert result.table_schema_properties[0].value_url == "some-dimension.csv#code-list"
    assert result.table_schema_properties[0].primary_key_col_names == "uri_identifier"


def test_get_codelist_primary_key_by_csv_url():
    """
    Ensures that the correct primary key column name is returned given the input csv url.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "some-dimension.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)

    csvw_inspector: CsvWInspector = CsvWInspector(
        csvw_rdf_manager.rdf_graph, csvw_metadata_json_path
    )

    result = csvw_inspector.get_codelist_primary_key_by_csv_url()

    assert len(result.primary_key_col_names) == 1
    assert result.primary_key_col_names[0].value == "uri_identifier"
