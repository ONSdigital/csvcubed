import os

from csvcubed.cli.inspect.metadatainputvalidator import MetadataValidator
from csvcubed.cli.inspect.metadataprinter import MetadataPrinter
from csvcubed.models.sparqlresults import DSDLabelURIResult
from csvcubed.utils.tableschema import CsvwRdfManager
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_pivoted_shape():
    os.environ["PIVOTED_MULTI_MEASURE"] = "True"

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-shape-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )
    (
        _,
        csvw_type,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    metadata_printer = MetadataPrinter(
        csvw_type, csvw_metadata_rdf_graph, csvw_metadata_json_path
    )
    dsd_info_printable = metadata_printer.dsd_info_printable

    assert dsd_info_printable is not None
    
    del os.environ["PIVOTED_MULTI_MEASURE"]