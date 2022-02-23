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

    metadata_printer = MetadataPrinter(
        csvw_type, csvw_metadata_rdf_graph, csvw_metadata_json_path
    )
    printable = metadata_printer.gen_type_info_printable()

    assert printable == "\u2022 This file is a data cube."


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

    metadata_printer = MetadataPrinter(
        csvw_type, csvw_metadata_rdf_graph, csvw_metadata_json_path
    )
    printable = metadata_printer.gen_type_info_printable()

    assert printable == "\u2022 This file is a code list."


def test_csvw_catalog_metadata_printable_datacube():
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

    metadata_printer = MetadataPrinter(
        csvw_type, csvw_metadata_rdf_graph, csvw_metadata_json_path
    )
    printable = metadata_printer.gen_catalog_metadata_printable()
    printable = printable.replace("\t", "").replace("\n", "")

    assert (
        printable
        == "\u2022 The data cube has the following catalog metadata: - Title: Alcohol Bulletin- Label: Alcohol Bulletin- Issued: 2016-02-26T09:30:00+00:00- Modified: 2022-02-11T21:00:09.286102+00:00- License: None- Creator: https://www.gov.uk/government/organisations/hm-revenue-customs- Publisher: https://www.gov.uk/government/organisations/hm-revenue-customs- Landing Pages: -- https://www.gov.uk/government/statistics/alcohol-bulletin- Themes: -- http://gss-data.org.uk/def/gdp#trade- Keywords: None- Contact Point: None- Identifier: Alcohol Bulletin- Comment: Quarterly statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs.- Description: The Alcohol Bulletin National Statistics present statistics from the 4different alcohol duties administered by HM Revenue and Customs (HMRC): [WineDuty](https://www.gov.uk/government/collections/wine-duty) (wine and made-wine), [Spirits Duty](https://www.gov.uk/guidance/spirits-duty), [BeerDuty](https://www.gov.uk/guidance/beer-duty) and [CiderDuty](https://www.gov.uk/government/collections/cider-duty).The Alcohol Bulletin is updated quarterly and includes statistics on dutyreceipts up to the latest full month before its release, and statisticsrelating to clearances and production that are one month behind that of dutyreceipts.[Archive versions of the Alcohol Bulletin published on GOV.UK after August2019](https://webarchive.nationalarchives.gov.uk/ukgwa/*/https://www.gov.uk/government/statistics/alcohol-bulletin) are no longer hosted on this page and are instead available via theUK Government Web Archive, from the National Archives.[Archive versions of the Alcohol Bulletin published between 2008 and August2019](https://www.uktradeinfo.com/trade-data/tax-and-duty-bulletins/) arefound on the UK Trade Info website.## Quality reportFurther details for this statistical release, including data suitability andcoverage, are included within the [Alcohol Bulletin qualityreport](https://www.gov.uk/government/statistics/quality-report-alcohol-duties-publications-bulletin-and-factsheet).  *[HMRC]: HM Revenue and Customs  *[UK]: United Kingdom"
    )


def test_csvw_catalog_metadata_printable_codelist():
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

    metadata_printer = MetadataPrinter(
        csvw_type, csvw_metadata_rdf_graph, csvw_metadata_json_path
    )
    printable = metadata_printer.gen_catalog_metadata_printable()
    printable = printable.replace("\t", "").replace("\n", "")

    assert (
        printable
        == "\u2022 The code list has the following catalog metadata: - Title: Alcohol Content- Label: Alcohol Content- Issued: 2022-02-11T21:00:21.040987- Modified: 2022-02-11T21:00:21.040987- License: None- Creator: None- Publisher: None- Landing Pages: None- Themes: None- Keywords: None- Contact Point: None- Identifier: Alcohol Content- Comment: None- Description: None"
    )


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

    metadata_printer = MetadataPrinter(
        csvw_type, csvw_metadata_rdf_graph, csvw_metadata_json_path
    )
    printable = metadata_printer.gen_dsd_info_printable()
    printable = printable.replace("\t", "").replace("\n", "")

    #TODO: Format string and do assert.
    assert printable == printable
