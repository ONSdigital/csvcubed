from csvcubed.cli.inspect.metadatainputvalidator import CSVWType, MetadataValidator
from csvcubed.cli.inspect.metadataprocessor import MetadataProcessor
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_detect_valid_csvw_metadata_datacube_input():
    """
    Should return true if the csv-w metadata input is a data cube or code list.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)

    (
        valid_csvw_metadata_datacube,
        _,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    assert valid_csvw_metadata_datacube == True


def test_detect_valid_csvw_metadata_codelist_input():
    """
    Should return true if the csv-w metadata input is a data cube or code list.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)

    (
        valid_csvw_metadata_codelist,
        _,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    assert valid_csvw_metadata_codelist == True


def test_detect_invalid_csvw_metadata_input():
    """
    Should return false if the csv-w metadata input is not a data cube or code list.
    """

    csvw_metadata_json_path = _test_case_base_dir / "json.table.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)

    (
        valid_csvw_metadata,
        _,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    assert valid_csvw_metadata == False


def test_detect_type_datacube():
    """
    Should return CSVWType.QbDataSet is the input csv-w is a db:Dataset.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)

    (
        _,
        csvw_type,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    assert csvw_type == CSVWType.QbDataSet


def test_detect_type_codelist():
    """
    Should return CSVWType.CodeList is the input csv-w is a skos:ConceptScheme.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)

    (
        _,
        csvw_type,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    assert csvw_type == CSVWType.CodeList


def test_detect_type_other():
    """
    Should return CSVWType.Other is the input csv-w is neither a db:Dataset nor a skos:ConceptScheme.
    """
    csvw_metadata_json_path = _test_case_base_dir / "json.table.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)

    (
        _,
        csvw_type,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    assert csvw_type == CSVWType.Other
