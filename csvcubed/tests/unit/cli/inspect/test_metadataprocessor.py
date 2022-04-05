from csvcubedmodels.rdf.namespaces import CSVW
from rdflib import Literal

from csvcubed.cli.inspect.metadataprocessor import MetadataProcessor
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"
_csvw_test_cases_dir = get_test_cases_dir() / "utils" / "csvw"


def test_metadata_dataset_json_ld_to_rdf_loading():
    """
    Metadata dataset RDF graph should not be None.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    assert csvw_metadata_rdf_graph is not None
    assert any(csvw_metadata_rdf_graph)


def test_metadata_codelist_json_ld_to_rdf_loading_with_table_schema():
    """
    Metadata codelist RDF graph should not be None.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    assert csvw_metadata_rdf_graph is not None
    assert any(csvw_metadata_rdf_graph)


def test_load_table_schema_file_dependencies_to_graph():
    """
    Test that the we can correctly load CSV-W tableSchema file dependencies with the MetadataProcessor.
    """

    csvw_metadata_json_path = (
        _csvw_test_cases_dir
        / "table-schema-dependencies"
        / "sectors-economic-estimates-2018-trade-in-services.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

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
