from csvcubed.cli.inspect.metadataprocessor import MetadataProcessor
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


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


# TODO: implement below after adding sparql for getting tableschema.
# def test_metadata_codelist_json_ld_to_rdf_loading_without_table_schema():
#     """
#     Metadata codelist RDF graph should not be None.
#     """
#     raise NotImplementedError()


def test_load_table_schema_file_dependencies_to_graph():
    """
    Test that the we can correctly load CSV-W tableSchema file dependencies with the MetadataProcessor.
    """
    from csvcubedmodels.rdf.namespaces import CSVW

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "table-schema-dependencies"
        / "sectors-economic-estimates-2018-trade-in-services.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    # This triple is defined in subsector.table.json
    assert (
        None,
        CSVW.aboutUrl,
        "subsector.csv#{+notation}",
    ) in csvw_metadata_rdf_graph

    # This triple is defined in sector.table.json
    assert (
        None,
        CSVW.aboutUrl,
        "sector.csv#{+notation}",
    ) in csvw_metadata_rdf_graph
