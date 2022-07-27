from csvcubedmodels.rdf.namespaces import CSVW
from rdflib import Literal, URIRef

from csvcubed.utils.tableschema import CsvwRdfManager
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"
_csvw_test_cases_dir = get_test_cases_dir() / "utils" / "csvw"


def test_metadata_dataset_json_ld_to_rdf_loading():
    """
    Metadata dataset RDF graph should not be None.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    table_schema_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = table_schema_manager.load_json_ld_to_rdflib_graph()

    assert csvw_metadata_rdf_graph is not None
    assert any(csvw_metadata_rdf_graph)


def test_metadata_dataset_json_ld_to_rdf_loading_when_path_contains_url_encodable_chars():
    """
    Metadata dataset RDF graph should not be None when the path contains url encodable chars.
    """
    dir_path = _test_case_base_dir / "url_enc@dable_char_@2path"
    csvw_metadata_json_path = dir_path / "alcohol-bulletin.csv-metadata.json"

    table_schema_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = table_schema_manager.load_json_ld_to_rdflib_graph()

    assert csvw_metadata_rdf_graph is not None
    assert any(csvw_metadata_rdf_graph)

    assert (
        URIRef("alcohol-bulletin.csv#component/alcohol-sub-type"),
        None,
        None,
    ) in csvw_metadata_rdf_graph


def test_metadata_codelist_json_ld_to_rdf_loading_with_table_schema():
    """
    Metadata codelist RDF graph should not be None.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    table_schema_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = table_schema_manager.load_json_ld_to_rdflib_graph()

    assert csvw_metadata_rdf_graph is not None
    assert any(csvw_metadata_rdf_graph)


def test_load_table_schema_file_dependencies_to_graph():
    """
    Test that the we can correctly load CSV-W tableSchema file dependencies with the CsvwRdfManager.
    """

    csvw_metadata_json_path = (
        _csvw_test_cases_dir
        / "table-schema-dependencies"
        / "sectors-economic-estimates-2018-trade-in-services.csv-metadata.json"
    )
    table_schema_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = table_schema_manager.load_json_ld_to_rdflib_graph()

    # This triple is defined in subsector.table.json
    assert (
        None,
        CSVW.aboutUrl,
        Literal("subsector.csv#{+notation}", datatype=CSVW.uriTemplate),
    ) in csvw_metadata_rdf_graph

    # This triple is defined in sector.table.json
    assert (
        None,
        CSVW.aboutUrl,
        Literal("sector.csv#{+notation}", datatype=CSVW.uriTemplate),
    ) in csvw_metadata_rdf_graph
