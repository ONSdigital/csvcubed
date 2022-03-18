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


# TODO: implement below after adding sparkl for getting tableschema.
# def test_metadata_codelist_json_ld_to_rdf_loading_without_table_schema():
#     """
#     Metadata codelist RDF graph should not be None.
#     """
#     raise NotImplementedError()
