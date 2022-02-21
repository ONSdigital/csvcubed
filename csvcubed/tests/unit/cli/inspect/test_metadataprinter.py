import json

from csvcubed.cli.inspect.metadatainputvalidator import MetadataValidator
from csvcubed.cli.inspect.metadataprinter import MetadataPrinter
from csvcubed.cli.inspect.metadataprocessor import MetadataProcessor
from csvcubed.utils.qb.components import ComponentPropertyType
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_csvw_type_info_printable_datacube():
    """
    Should return csvw type printable: This file is a data cube.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)

    (
        _,
        csvw_type,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    metadata_printer = MetadataPrinter(csvw_metadata_rdf_graph, csvw_type)
    printable = metadata_printer.gen_type_info_printable()

    assert printable == "This file is a data cube."


def test_csvw_type_info_printable_codelist():
    """
    Should return csvw type printable: This file is a code list.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)

    (
        _,
        csvw_type,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    metadata_printer = MetadataPrinter(csvw_metadata_rdf_graph, csvw_type)
    printable = metadata_printer.gen_type_info_printable()

    assert printable == "This file is a code list."


def test_csvw_metadata_info_printable_datacube_():
    """
    Should contain metadata information for the given data cube.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)

    (
        _,
        csvw_type,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    metadata_printer = MetadataPrinter(csvw_metadata_rdf_graph, csvw_type)
    printable = metadata_printer.gen_metadata_info_printable()
    printable_json = json.loads(printable)

    assert printable_json["title"] == "Alcohol Bulletin"
    assert printable_json["label"] == "Alcohol Bulletin"
    assert printable_json["issued"] == "2016-02-26 09:30:00+00:00"
    assert printable_json["modified"] == "2022-02-11 21:00:09.286102+00:00"
    assert (
        printable_json["comment"]
        == "Quarterly statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs."
    )
    assert (
        printable_json["description"]
        == "The Alcohol Bulletin National Statistics present statistics from the 4\ndifferent alcohol duties administered by HM Revenue and Customs (HMRC): [Wine\nDuty](https://www.gov.uk/government/collections/wine-duty) (wine and made-\nwine), [Spirits Duty](https://www.gov.uk/guidance/spirits-duty), [Beer\nDuty](https://www.gov.uk/guidance/beer-duty) and [Cider\nDuty](https://www.gov.uk/government/collections/cider-duty).\n\nThe Alcohol Bulletin is updated quarterly and includes statistics on duty\nreceipts up to the latest full month before its release, and statistics\nrelating to clearances and production that are one month behind that of duty\nreceipts.\n\n[Archive versions of the Alcohol Bulletin published on GOV.UK after August\n2019](https://webarchive.nationalarchives.gov.uk/ukgwa/*/https://www.gov.uk/government/statistics/alcohol-\nbulletin) are no longer hosted on this page and are instead available via the\nUK Government Web Archive, from the National Archives.\n\n[Archive versions of the Alcohol Bulletin published between 2008 and August\n2019](https://www.uktradeinfo.com/trade-data/tax-and-duty-bulletins/) are\nfound on the UK Trade Info website.\n\n## Quality report\n\nFurther details for this statistical release, including data suitability and\ncoverage, are included within the [Alcohol Bulletin quality\nreport](https://www.gov.uk/government/statistics/quality-report-alcohol-\nduties-publications-bulletin-and-factsheet).\n\n  *[HMRC]: HM Revenue and Customs\n  *[UK]: United Kingdom\n\n"
    )
    assert printable_json["license"] is None
    assert (
        printable_json["creator"]
        == "https://www.gov.uk/government/organisations/hm-revenue-customs"
    )
    assert (
        printable_json["publisher"]
        == "https://www.gov.uk/government/organisations/hm-revenue-customs"
    )
    assert (
        len(printable_json["landing_pages"]) == 1
        and printable_json["landing_pages"][0]
        == "https://www.gov.uk/government/statistics/alcohol-bulletin"
    )
    assert (
        len(printable_json["themes"]) == 1
        and printable_json["themes"][0] == "http://gss-data.org.uk/def/gdp#trade"
    )
    assert len(printable_json["keywords"]) == 0
    assert printable_json["contact_point"] is None
    assert printable_json["identifier"] == "Alcohol Bulletin"


def test_csvw_metadata_info_printable_codelist_():
    """
    Should contain metadata information for the given code list.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)

    (
        _,
        csvw_type,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    metadata_printer = MetadataPrinter(csvw_metadata_rdf_graph, csvw_type)
    printable = metadata_printer.gen_metadata_info_printable()
    printable_json = json.loads(printable)

    assert printable_json["title"] == "Alcohol Content"
    assert printable_json["label"] == "Alcohol Content"
    assert printable_json["issued"] == "2022-02-11 21:00:21.040987"
    assert printable_json["modified"] == "2022-02-11 21:00:21.040987"
    assert printable_json["comment"] is None
    assert printable_json["description"] is None
    assert printable_json["license"] is None
    assert printable_json["creator"] is None
    assert printable_json["publisher"] is None
    assert len(printable_json["landing_pages"]) == 0
    assert len(printable_json["themes"]) == 0
    assert len(printable_json["keywords"]) == 0
    assert printable_json["contact_point"] is None
    assert printable_json["identifier"] == "Alcohol Content"


def test_csvw_dsd_info_printable_datacube():
    """
    Should contain dataset label, qube components and cols with suppress output for the given data cube.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)

    (
        _,
        csvw_type,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    metadata_printer = MetadataPrinter(csvw_metadata_rdf_graph, csvw_type)
    printable = metadata_printer.gen_dsd_info_printable()
    printable_json = json.loads(printable)

    assert printable_json["dataset_label"] == "Alcohol Bulletin"
    assert printable_json["num_of_components"] == 17

    assert printable_json["components"][0] is not None
    assert (
        printable_json["components"][0]["componentProperty"]
        == "http://purl.org/linked-data/sdmx/2009/dimension#refPeriod"
    )
    assert printable_json["components"][0]["componentPropertyLabel"] is None
    assert (
        printable_json["components"][0]["componentPropertyType"]
        == ComponentPropertyType.Dimension.value
    )
    assert printable_json["components"][0]["csvColumnTitle"] is None
    assert printable_json["components"][0]["required"] is None


def test_csvw_dsd_info_printable_codelist():
    """
    Should contain N/A for the given code list.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)

    (
        _,
        csvw_type,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    metadata_printer = MetadataPrinter(csvw_metadata_rdf_graph, csvw_type)
    printable = metadata_printer.gen_dsd_info_printable()

    assert printable == "N/A"
