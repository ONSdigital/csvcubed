import dateutil.parser

from csvcubed.cli.inspect.inspectsparqlmanager import (
    ask_is_csvw_code_list,
    ask_is_csvw_qb_dataset,
    select_cols_w_supress_output,
    select_csvw_catalog_metadata,
    select_csvw_dsd_dataset_label_and_dsd_def_uri,
    select_csvw_dsd_qube_components,
)
from csvcubed.cli.inspect.metadatainputvalidator import MetadataValidator
from csvcubed.cli.inspect.metadataprocessor import MetadataProcessor
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_ask_is_csvw_code_list():
    """
    Should return true if the input rdf graph is a code list.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    is_code_list = ask_is_csvw_code_list(csvw_metadata_rdf_graph)

    assert is_code_list == True


def test_ask_is_csvw_qb_dataset():
    """
    Should return true if the input rdf graph is a qb dataset.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    is_qb_dataset = ask_is_csvw_qb_dataset(csvw_metadata_rdf_graph)

    assert is_qb_dataset == True


def test_select_csvw_catalog_metadata_for_dataset():
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result = select_csvw_catalog_metadata(csvw_metadata_rdf_graph)
    info_dict = result.asdict()

    assert str(info_dict["title"]) == "Alcohol Bulletin"
    assert str(info_dict["label"]) == "Alcohol Bulletin"
    assert (
        dateutil.parser.isoparse(info_dict["issued"]).strftime("%Y-%m-%d %H:%M:%S%z")
        == "2016-02-26 09:30:00+0000"
    )
    assert (
        dateutil.parser.isoparse(info_dict["modified"]).strftime("%Y-%m-%d %H:%M:%S%z")
        == "2022-02-11 21:00:09+0000"
    )
    assert (
        str(info_dict.get("comment"))
        == "Quarterly statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs."
    )
    assert (
        str(info_dict.get("description"))
        == "The Alcohol Bulletin National Statistics present statistics from the 4\ndifferent alcohol duties administered by HM Revenue and Customs (HMRC): [Wine\nDuty](https://www.gov.uk/government/collections/wine-duty) (wine and made-\nwine), [Spirits Duty](https://www.gov.uk/guidance/spirits-duty), [Beer\nDuty](https://www.gov.uk/guidance/beer-duty) and [Cider\nDuty](https://www.gov.uk/government/collections/cider-duty).\n\nThe Alcohol Bulletin is updated quarterly and includes statistics on duty\nreceipts up to the latest full month before its release, and statistics\nrelating to clearances and production that are one month behind that of duty\nreceipts.\n\n[Archive versions of the Alcohol Bulletin published on GOV.UK after August\n2019](https://webarchive.nationalarchives.gov.uk/ukgwa/*/https://www.gov.uk/government/statistics/alcohol-\nbulletin) are no longer hosted on this page and are instead available via the\nUK Government Web Archive, from the National Archives.\n\n[Archive versions of the Alcohol Bulletin published between 2008 and August\n2019](https://www.uktradeinfo.com/trade-data/tax-and-duty-bulletins/) are\nfound on the UK Trade Info website.\n\n## Quality report\n\nFurther details for this statistical release, including data suitability and\ncoverage, are included within the [Alcohol Bulletin quality\nreport](https://www.gov.uk/government/statistics/quality-report-alcohol-\nduties-publications-bulletin-and-factsheet).\n\n  *[HMRC]: HM Revenue and Customs\n  *[UK]: United Kingdom\n\n"
    )
    assert info_dict.get("licence") is None
    assert (
        str(info_dict.get("creator"))
        == "https://www.gov.uk/government/organisations/hm-revenue-customs"
    )
    assert (
        str(info_dict.get("publisher"))
        == "https://www.gov.uk/government/organisations/hm-revenue-customs"
    )
    assert (
        len(info_dict["landingPages"].split("|")) == 1
        and info_dict["landingPages"].split("|")[0]
        == "https://www.gov.uk/government/statistics/alcohol-bulletin"
    )
    assert (
        len(info_dict["themes"].split("|")) == 1
        and info_dict["themes"].split("|")[0] == "http://gss-data.org.uk/def/gdp#trade"
    )
    assert len(info_dict["keywords"]) == 0
    assert info_dict.get("contactPoint") is None
    assert str(info_dict["identifier"]) == "Alcohol Bulletin"


def test_select_csvw_catalog_metadata_for_codelist():
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result = select_csvw_catalog_metadata(csvw_metadata_rdf_graph)
    info_dict = result.asdict()

    assert str(info_dict["title"]) == "Alcohol Content"
    assert str(info_dict["label"]) == "Alcohol Content"
    assert (
        dateutil.parser.isoparse(info_dict["issued"]).strftime("%Y-%m-%d %H:%M:%S.%f%Z")
        == "2022-02-11 21:00:21.040987"
    )
    assert (
        dateutil.parser.isoparse(info_dict["modified"]).strftime(
            "%Y-%m-%d %H:%M:%S.%f%Z"
        )
        == "2022-02-11 21:00:21.040987"
    )
    assert info_dict.get("comment") is None
    assert info_dict.get("description") is None
    assert info_dict.get("license") is None
    assert info_dict.get("creator") is None
    assert info_dict.get("publisher") is None
    assert len(info_dict["landingPages"]) == 0
    assert len(info_dict["themes"]) == 0
    assert len(info_dict["keywords"]) == 0
    assert info_dict.get("contactPoint") is None
    assert str(info_dict.get("identifier")) == "Alcohol Content"


def test_select_csvw_dsd_dataset():
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result = select_csvw_dsd_dataset_label_and_dsd_def_uri(csvw_metadata_rdf_graph)
    result_dict = result.asdict()
    components = select_csvw_dsd_qube_components(
        csvw_metadata_rdf_graph, result_dict["dataStructureDefinition"]
    )

    assert str(result_dict["dataSetLabel"]) == "Alcohol Bulletin"
    assert len(components) == 17


def test_select_cols_when_supress_output_cols_not_present():
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    results = select_cols_w_supress_output(csvw_metadata_rdf_graph)
    assert len(results) == 0


def test_select_cols_when_supress_output_cols_present():
    csvw_metadata_json_path = (
        _test_case_base_dir / "datacube_with_suppress_output_cols.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    results = select_cols_w_supress_output(csvw_metadata_rdf_graph)
    assert len(results) == 1
