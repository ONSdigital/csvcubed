from pathlib import Path

import pytest
from csvcubed.utils.iterables import first

from csvcubed.utils.sparql import path_to_file_uri_for_rdflib
import dateutil.parser
from rdflib import Graph, RDF, DCAT, URIRef, RDFS, Literal, ConjunctiveGraph

from csvcubed.models.inspectsparqlresults import (
    CatalogMetadataResult,
    CodeListColsByDatasetUrlResult,
    CodelistsResult,
    ColsWithSuppressOutputTrueResult,
    DSDLabelURIResult,
    DSDSingleUnitResult,
    DatasetURLResult,
    QubeComponentsResult,
    MetadataDependenciesResult,
)
from csvcubed.utils.qb.components import ComponentPropertyType
from csvcubed.cli.inspect.inspectsparqlmanager import (
    ask_is_csvw_code_list,
    ask_is_csvw_qb_dataset,
    select_codelist_cols_by_dataset_url,
    select_codelist_dataset_url,
    select_cols_where_suppress_output_is_true,
    select_csvw_catalog_metadata,
    select_csvw_dsd_dataset_label_and_dsd_def_uri,
    select_csvw_dsd_qube_components,
    select_dsd_code_list_and_cols,
    select_qb_dataset_url,
    select_csvw_table_schema_file_dependencies,
    select_single_unit_from_dsd,
    select_metadata_dependencies,
)
from csvcubed.cli.inspect.metadataprocessor import (
    MetadataProcessor,
    add_triples_for_file_dependencies,
)
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"
_csvw_test_cases_dir = get_test_cases_dir() / "utils" / "csvw"


def test_ask_is_csvw_code_list():
    """
    Should return true if the input rdf graph is a code list.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    is_code_list = ask_is_csvw_code_list(csvw_metadata_rdf_graph)

    assert is_code_list is True


def test_ask_is_csvw_qb_dataset():
    """
    Should return true if the input rdf graph is a qb dataset.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    is_qb_dataset = ask_is_csvw_qb_dataset(csvw_metadata_rdf_graph)

    assert is_qb_dataset is True


def test_select_csvw_catalog_metadata_for_dataset():
    """
    Should return expected `CatalogMetadataResult`.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result: CatalogMetadataResult = select_csvw_catalog_metadata(
        csvw_metadata_rdf_graph
    )

    assert result.dataset_uri == "alcohol-bulletin.csv#dataset"
    assert result.title == "Alcohol Bulletin"
    assert result.label == "Alcohol Bulletin"
    assert (
        dateutil.parser.isoparse(result.issued).strftime("%Y-%m-%d %H:%M:%S%z")
        == "2016-02-26 09:30:00+0000"
    )
    assert (
        dateutil.parser.isoparse(result.modified).strftime("%Y-%m-%d %H:%M:%S%z")
        == "2022-02-11 21:00:09+0000"
    )
    assert (
        result.comment
        == "Quarterly statistics from the 4 different alcohol duty regimes administered by HM Revenue and Customs."
    )
    assert (
        result.description
        == "The Alcohol Bulletin National Statistics present statistics from the 4\ndifferent alcohol duties administered by HM Revenue and Customs (HMRC): [Wine\nDuty](https://www.gov.uk/government/collections/wine-duty) (wine and made-\nwine), [Spirits Duty](https://www.gov.uk/guidance/spirits-duty), [Beer\nDuty](https://www.gov.uk/guidance/beer-duty) and [Cider\nDuty](https://www.gov.uk/government/collections/cider-duty).\n\nThe Alcohol Bulletin is updated quarterly and includes statistics on duty\nreceipts up to the latest full month before its release, and statistics\nrelating to clearances and production that are one month behind that of duty\nreceipts.\n\n[Archive versions of the Alcohol Bulletin published on GOV.UK after August\n2019](https://webarchive.nationalarchives.gov.uk/ukgwa/*/https://www.gov.uk/government/statistics/alcohol-\nbulletin) are no longer hosted on this page and are instead available via the\nUK Government Web Archive, from the National Archives.\n\n[Archive versions of the Alcohol Bulletin published between 2008 and August\n2019](https://www.uktradeinfo.com/trade-data/tax-and-duty-bulletins/) are\nfound on the UK Trade Info website.\n\n## Quality report\n\nFurther details for this statistical release, including data suitability and\ncoverage, are included within the [Alcohol Bulletin quality\nreport](https://www.gov.uk/government/statistics/quality-report-alcohol-\nduties-publications-bulletin-and-factsheet).\n\n  *[HMRC]: HM Revenue and Customs\n  *[UK]: United Kingdom\n\n"
    )
    assert result.license == "None"
    assert (
        result.creator
        == "https://www.gov.uk/government/organisations/hm-revenue-customs"
    )
    assert (
        result.publisher
        == "https://www.gov.uk/government/organisations/hm-revenue-customs"
    )
    assert (
        len(result.landing_pages) == 1
        and result.landing_pages[0]
        == "https://www.gov.uk/government/statistics/alcohol-bulletin"
    )
    assert (
        len(result.themes) == 1
        and result.themes[0] == "http://gss-data.org.uk/def/gdp#trade"
    )
    assert len(result.keywords) == 1 and result.keywords[0] == ""
    assert result.contact_point == "None"
    assert result.identifier == "Alcohol Bulletin"


def test_select_csvw_catalog_metadata_for_codelist():
    """
    Should return expected `CatalogMetadataResult`.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result: CatalogMetadataResult = select_csvw_catalog_metadata(
        csvw_metadata_rdf_graph
    )

    assert result.title == "Alcohol Content"
    assert result.label == "Alcohol Content"
    assert (
        dateutil.parser.isoparse(result.issued).strftime("%Y-%m-%d %H:%M:%S.%f%Z")
        == "2022-02-11 21:00:21.040987"
    )
    assert (
        dateutil.parser.isoparse(result.modified).strftime("%Y-%m-%d %H:%M:%S.%f%Z")
        == "2022-02-11 21:00:21.040987"
    )
    assert result.comment == "None"
    assert result.description == "None"
    assert result.license == "None"
    assert result.creator == "None"
    assert result.publisher == "None"
    assert len(result.landing_pages) == 1 and result.landing_pages[0] == ""
    assert len(result.themes) == 1 and result.themes[0] == ""
    assert len(result.keywords) == 1 and result.keywords[0] == ""
    assert result.contact_point == "None"
    assert result.identifier == "Alcohol Content"


def test_select_csvw_dsd_dataset():
    """
    Should return expected `DSDLabelURIResult`.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result: DSDLabelURIResult = select_csvw_dsd_dataset_label_and_dsd_def_uri(
        csvw_metadata_rdf_graph
    )
    component_result: QubeComponentsResult = select_csvw_dsd_qube_components(
        csvw_metadata_rdf_graph, result.dsd_uri, csvw_metadata_json_path
    )
    components = component_result.qube_components

    assert result.dataset_label == "Alcohol Bulletin"
    assert len(components) == 17
    assert (
        components[0].property
        == "http://purl.org/linked-data/sdmx/2009/dimension#refPeriod"
    )
    assert components[0].property_label == ""
    assert components[0].property_type == ComponentPropertyType.Dimension.value
    assert components[0].csv_col_title == "Period"
    assert components[0].required is True


def test_select_cols_when_supress_output_cols_not_present():
    """
    Should return expected `ColsWithSuppressOutputTrueResult`.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result: ColsWithSuppressOutputTrueResult = (
        select_cols_where_suppress_output_is_true(csvw_metadata_rdf_graph)
    )
    assert len(result.columns) == 0


def test_select_cols_when_supress_output_cols_present():
    """
    Should return expected `ColsWithSuppressOutputTrueResult`.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir / "datacube_with_suppress_output_cols.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result: ColsWithSuppressOutputTrueResult = (
        select_cols_where_suppress_output_is_true(csvw_metadata_rdf_graph)
    )
    assert len(result.columns) == 2
    assert set(result.columns) == {"Col1WithSuppressOutput", "Col2WithSuppressOutput"}


def test_select_dsd_code_list_and_cols_without_codelist_labels():
    """
    Should return expected `DSDLabelURIResult`.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result_dsd: DSDLabelURIResult = select_csvw_dsd_dataset_label_and_dsd_def_uri(
        csvw_metadata_rdf_graph
    )

    result: CodelistsResult = select_dsd_code_list_and_cols(
        csvw_metadata_rdf_graph, result_dsd.dsd_uri, csvw_metadata_json_path
    )

    assert len(result.codelists) == 3
    assert (
        first(result.codelists, lambda c: c.cols_used_in == "Alcohol Sub Type")
        is not None
    )


def test_select_qb_dataset_url():
    """
    Should return expected `DatasetURLResult`.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    result: DatasetURLResult = select_qb_dataset_url(
        csvw_metadata_rdf_graph,
        f"file://{str(_test_case_base_dir)}/alcohol-bulletin.csv#dataset",
    )
    assert result.dataset_url == "alcohol-bulletin.csv"


def test_select_single_unit_from_dsd():
    """
    Should return expected `DSDSingleUnitResult`.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_multi-measure"
        / "final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv-metadata.json"
    )
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    dataset_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri

    result: DSDSingleUnitResult = select_single_unit_from_dsd(
        csvw_metadata_rdf_graph, dataset_uri, csvw_metadata_json_path
    )
    assert result.unit_label == "MtCO2e"
    assert (
        result.unit_uri
        == "final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#unit/mtco2e"
    )


def test_select_table_schema_dependencies():
    """
    Test that we can successfully identify all table schema file dependencies from a CSV-W.

    This test ensures that table schemas defined in-line are not returned and are handled gracefully.
    """
    table_schema_dependencies_dir = _csvw_test_cases_dir / "table-schema-dependencies"
    csvw_metadata_json_path = (
        table_schema_dependencies_dir
        / "sectors-economic-estimates-2018-trade-in-services.csv-metadata.json"
    )

    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    table_schema_results = select_csvw_table_schema_file_dependencies(
        csvw_metadata_rdf_graph
    )

    assert set(table_schema_results.table_schema_file_dependencies) == {
        "sector.table.json",
        "subsector.table.json",
    }


def test_select_codelist_cols_by_dataset_url():
    """
    Should return expected `CodeListColsByDatasetUrlResult`.
    """
    csvw_metadata_json_path = _test_case_base_dir / "alcohol-content.csv-metadata.json"
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    dataset_url = select_codelist_dataset_url(csvw_metadata_rdf_graph).dataset_url

    result: CodeListColsByDatasetUrlResult = select_codelist_cols_by_dataset_url(
        csvw_metadata_rdf_graph, dataset_url
    )

    assert len(result.columns) == 7

    assert result.columns[0].column_title == "Label"
    assert result.columns[0].column_property_url == "rdfs:label"
    assert result.columns[0].column_value_url is None

    assert result.columns[1].column_title == "Notation"
    assert result.columns[1].column_property_url == "skos:notation"
    assert result.columns[1].column_value_url is None

    assert result.columns[2].column_title == "Parent Notation"
    assert result.columns[2].column_property_url == "skos:broader"
    assert (
        result.columns[2].column_value_url == "alcohol-content.csv#{+parent_notation}"
    )

    assert result.columns[3].column_title == "Sort Priority"
    assert (
        result.columns[3].column_property_url == "http://www.w3.org/ns/ui#sortPriority"
    )
    assert result.columns[3].column_value_url is None

    assert result.columns[4].column_title == "Description"
    assert result.columns[4].column_property_url == "rdfs:comment"
    assert result.columns[4].column_value_url is None

    assert result.columns[5].column_title is None
    assert result.columns[5].column_property_url == "skos:inScheme"
    assert result.columns[5].column_value_url == "alcohol-content.csv#code-list"

    assert result.columns[6].column_title is None
    assert result.columns[6].column_property_url == "rdf:type"
    assert result.columns[6].column_value_url == "skos:Concept"


def test_select_metadata_dependencies() -> None:
    """
    Test that we can extract `void:DataSet` dependencies from a csvcubed CSV-W output.
    """

    metadata_file = _test_case_base_dir / "dependencies" / "data.csv-metadata.json"
    data_file = _test_case_base_dir / "dependencies" / "data.csv"
    expected_dependency_file = (
        _test_case_base_dir / "dependencies" / "dimension.csv-metadata.json"
    )

    graph = Graph()
    graph.load(metadata_file, format="json-ld")
    dependencies = select_metadata_dependencies(graph)

    assert len(dependencies) == 1
    dependency = dependencies[0]

    assert dependency == MetadataDependenciesResult(
        data_set=f"{path_to_file_uri_for_rdflib(data_file)}#dependency/dimension",
        data_dump=path_to_file_uri_for_rdflib(expected_dependency_file.absolute()),
        uri_space="dimension.csv#",
    )


def test_rdf_dependency_loaded() -> None:
    """
    Ensure that the MetadataProcessor loads dependent RDF graphs to get a complete picture of the cube's metadata.
    """
    dimension_data_file = _test_case_base_dir / "dependencies" / "dimension.csv"
    metadata_file = _test_case_base_dir / "dependencies" / "data.csv-metadata.json"

    metadata_processor = MetadataProcessor(metadata_file)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    # assert that the `<dimension.csv#code-list> a dcat:Dataset` triple has been loaded.
    # this triple lives in the dependent `dimension.csv-metadata.json` file.
    assert (
        URIRef("dimension.csv#code-list"),
        RDF.type,
        DCAT.Dataset,
    ) in csvw_metadata_rdf_graph


@pytest.mark.timeout(30)
def test_cyclic_rdf_dependencies_loaded() -> None:
    """
    Ensure that the MetadataProcessor loads dependent RDF graphs even when there is a cyclic dependency
    """
    metadata_file = _test_case_base_dir / "dependencies" / "cyclic.csv-metadata.json"

    metadata_processor = MetadataProcessor(metadata_file)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    # Assert that some RDF has been loaded.
    assert any(csvw_metadata_rdf_graph)


def test_transitive_rdf_dependency_loaded() -> None:
    """
    Ensure that the MetadataProcessor loads a transitive dependency.
     transitive.csv-metadata.json -> transitive.1.json -> transitive.2.json
    """
    metadata_file = (
        _test_case_base_dir / "dependencies" / "transitive.csv-metadata.json"
    )

    metadata_processor = MetadataProcessor(metadata_file)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    # Assert that some RDF has been loaded.
    assert (
        URIRef("http://example.com/transitive.2"),
        RDFS.label,
        Literal("This is in a transitive dependency"),
    ) in csvw_metadata_rdf_graph


def test_rdf_load_ttl_dependency() -> None:
    """
    Ensure that we can successfully load a turtle file as an RDF dependency.
    """
    metadata_file = _test_case_base_dir / "dependencies" / "turtle.csv-metadata.json"

    metadata_processor = MetadataProcessor(metadata_file)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    # Assert that some RDF has been loaded.
    assert (
        URIRef("http://example.com/turtle.1"),
        RDFS.label,
        Literal("This is in a turtle dependency"),
    ) in csvw_metadata_rdf_graph


@pytest.mark.vcr
def test_rdf_load_url_dependency() -> None:
    """
    Test that we can successfully load a URL-based dependency and have transitive relative dependencies work.
    """
    graph = ConjunctiveGraph()
    graph.get_context("Dynamic input").parse(
        data="""
        @prefix void: <http://rdfs.org/ns/void#>.
    
        <http://example.com/dependency> a void:Dataset;
             void:dataDump <https://raw.githubusercontent.com/GSS-Cogs/csvcubed/dc1b8df2cd306346e17778cb951417935c91e78b/tests/test-cases/cli/inspect/dependencies/transitive.1.json>;
             void:uriSpace "http://example.com/some-uri-prefix".
        """,
        format="ttl",
    )

    add_triples_for_file_dependencies(graph, Path("."))

    assert (
        URIRef("http://example.com/transitive.2"),
        RDFS.label,
        Literal("This is in a transitive dependency"),
    ) in graph
