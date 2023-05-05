from pathlib import Path
from typing import List, Optional

import dateutil.parser
import pytest
from rdflib import DCAT, RDF, RDFS, ConjunctiveGraph, Graph, Literal, URIRef

from csvcubed.models.sparqlresults import (
    CatalogMetadataResult,
    ColumnDefinition,
    CubeTableIdentifiers,
    IsPivotedShapeMeasureResult,
    MetadataDependenciesResult,
    QubeComponentResult,
    UnitResult,
)
from csvcubed.utils.iterables import first
from csvcubed.utils.qb.components import ComponentPropertyType
from csvcubed.utils.rdf import parse_graph_retain_relative
from csvcubed.utils.sparql_handler.sparqlquerymanager import (
    ask_is_csvw_code_list,
    ask_is_csvw_qb_dataset,
    select_csvw_table_schema_file_dependencies,
    select_is_pivoted_shape_for_measures_in_data_set,
    select_metadata_dependencies,
)
from csvcubed.utils.tableschema import add_triples_for_file_dependencies
from tests.helpers.repository_cache import (
    get_code_list_repository,
    get_csvw_rdf_manager,
    get_data_cube_repository,
)
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"
_csvw_test_cases_dir = get_test_cases_dir() / "utils" / "csvw"


def assert_dsd_component_equal(
    component: QubeComponentResult,
    property: str,
    property_type: ComponentPropertyType,
    property_label: str,
    csv_col_titles: List[str],
    observation_value_column_titles: List[str],
    dsd_uri: str,
    required: bool,
):
    assert component.property == property
    assert component.property_type == property_type.value
    assert component.property_label == property_label
    assert {c.title for c in component.real_columns_used_in} == set(csv_col_titles)
    assert component.dsd_uri == dsd_uri
    assert component.required == required

    if any(observation_value_column_titles):
        expected_obs_val_col_titles = {
            title.strip() for title in observation_value_column_titles
        }
        actual_obs_val_col_titles = {
            c.title.strip() for c in component.used_by_observed_value_columns
        }
        assert expected_obs_val_col_titles == actual_obs_val_col_titles


def _assert_code_list_column_equal(
    column: ColumnDefinition,
    column_title: Optional[str],
    column_property_url: str,
    column_value_url: Optional[str],
):
    assert (
        column.title == column_title
        if column_title is not None
        else column.title is None
    )
    assert column.property_url == column_property_url
    assert (
        column.value_url == column_value_url
        if column_value_url is not None
        else column.value_url is None
    )


def get_dsd_component_by_property_url(
    components: List[QubeComponentResult], property_url: str
) -> QubeComponentResult:
    """
    Filters dsd components by property url.
    """
    filtered_results = [
        component for component in components if component.property == property_url
    ]
    return filtered_results[0]


def _get_measure_by_measure_uri(
    results: List[IsPivotedShapeMeasureResult], measure_uri: str
) -> IsPivotedShapeMeasureResult:
    """
    Filters measures by measure uri.
    """
    filtered_results = [result for result in results if result.measure == measure_uri]
    assert len(filtered_results) == 1

    return filtered_results[0]


def _get_code_list_column_by_property_url(
    columns: List[ColumnDefinition], property_url: str
) -> ColumnDefinition:
    """
    Filters code list columns by column property url.
    """
    filtered_results = [
        result for result in columns if result.property_url == property_url
    ]
    assert len(filtered_results) == 1

    return filtered_results[0]


def test_ask_is_csvw_code_list():
    """
    Should return true if the input rdf graph is a code list.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    is_code_list = ask_is_csvw_code_list(csvw_metadata_rdf_graph)

    assert is_code_list is True


def test_ask_is_csvw_qb_dataset():
    """
    Should return true if the input rdf graph is a qb dataset.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    is_qb_dataset = ask_is_csvw_qb_dataset(csvw_metadata_rdf_graph)

    assert is_qb_dataset is True


def test_get_primary_catalog_metadata_for_dataset():
    """
    Should return expected `CatalogMetadataResult`.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)

    result: CatalogMetadataResult = (
        csvw_rdf_manager.csvw_repository.get_primary_catalog_metadata()
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


def test_select_single_unit_from_dsd():
    """
    Should return expected `UnitResult`.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_multi-measure"
        / "final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv-metadata.json"
    )
    data_cube_repository = get_data_cube_repository(csvw_metadata_json_path)

    result: UnitResult = data_cube_repository.get_unit_for_uri(
        "final-uk-greenhouse-gas-emissions-national-statistics-1990-to-2020.csv#unit/mtco2e"
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

    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    table_schema_results = select_csvw_table_schema_file_dependencies(
        csvw_metadata_rdf_graph
    )

    assert set(table_schema_results.table_schema_file_dependencies) == {
        "sector.table.json",
        "subsector.table.json",
    }


# Calling SPARQL query directly
def test_select_codelist_cols_by_csv_url():
    """
    Should return expected `CodeListColsByDatasetUrlResult`.
    """
    csvw_metadata_json_path = _test_case_base_dir / "alcohol-content.csv-metadata.json"
    code_list_repository = get_code_list_repository(csvw_metadata_json_path)
    primary_catalogue_metadata = (
        code_list_repository.csvw_repository.get_primary_catalog_metadata()
    )
    csv_url = code_list_repository.get_table_identifiers_for_concept_scheme(
        primary_catalogue_metadata.dataset_uri
    ).csv_url

    result = code_list_repository.csvw_repository.get_column_definitions_for_csv(
        csv_url
    )

    assert len(result) == 7

    column = _get_code_list_column_by_property_url(result, "rdfs:label")
    _assert_code_list_column_equal(column, "Label", "rdfs:label", None)

    column = _get_code_list_column_by_property_url(result, "skos:notation")
    _assert_code_list_column_equal(column, "Notation", "skos:notation", None)

    column = _get_code_list_column_by_property_url(result, "skos:broader")
    _assert_code_list_column_equal(
        column,
        "Parent Notation",
        "skos:broader",
        "alcohol-content.csv#{+parent_notation}",
    )

    column = _get_code_list_column_by_property_url(
        result, "http://www.w3.org/ns/ui#sortPriority"
    )
    _assert_code_list_column_equal(
        column, "Sort Priority", "http://www.w3.org/ns/ui#sortPriority", None
    )

    column = _get_code_list_column_by_property_url(result, "rdfs:comment")
    _assert_code_list_column_equal(column, "Description", "rdfs:comment", None)

    column = _get_code_list_column_by_property_url(result, "skos:inScheme")
    _assert_code_list_column_equal(
        column,
        None,
        "skos:inScheme",
        "alcohol-content.csv#code-list",
    )

    column = _get_code_list_column_by_property_url(result, "rdf:type")
    _assert_code_list_column_equal(column, None, "rdf:type", "skos:Concept")


# Calling SPARQL query directly
def test_select_metadata_dependencies():
    """
    Test that we can extract `void:DataSet` dependencies from a csvcubed CSV-W output.
    """

    metadata_file = _test_case_base_dir / "dependencies" / "data.csv-metadata.json"
    data_file = _test_case_base_dir / "dependencies" / "data.csv"
    expected_dependency_file = (
        _test_case_base_dir / "dependencies" / "dimension.csv-metadata.json"
    )

    graph = Graph()
    graph.parse(metadata_file, format="json-ld")
    dependencies = select_metadata_dependencies(graph)

    assert len(dependencies) == 1
    dependency = dependencies[0]

    assert dependency == MetadataDependenciesResult(
        data_set=f"{data_file.as_uri()}#dependency/dimension",
        data_dump=expected_dependency_file.absolute().as_uri(),
        uri_space="dimension.csv#",
    )


def test_select_is_pivoted_shape_for_measures_in_pivoted_shape_data_set():
    """
    Checks that the measures retrieved from a metadata file that represents a pivoted shape cube are as expected.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph
    results = select_is_pivoted_shape_for_measures_in_data_set(
        csvw_metadata_rdf_graph,
        [
            CubeTableIdentifiers(
                "qb-id-10003.csv",
                "qb-id-10003.csv#dataset",
                "qb-id-10003.csv#structure",
            )
        ],
    )

    assert results is not None
    assert len(results) == 2

    result = _get_measure_by_measure_uri(
        results, "qb-id-10003.csv#measure/some-measure"
    )
    assert result.measure == "qb-id-10003.csv#measure/some-measure"
    assert result.is_pivoted_shape == True

    result = _get_measure_by_measure_uri(
        results, "qb-id-10003.csv#measure/some-other-measure"
    )
    assert result.measure == "qb-id-10003.csv#measure/some-other-measure"
    assert result.is_pivoted_shape == True


# Calling SPARQL query directly
def test_select_is_pivoted_shape_for_measures_in_standard_shape_data_set():
    """
    Checks that the measures retrieved from a metadata file that represents a standard shape cube are as expected.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph
    results = select_is_pivoted_shape_for_measures_in_data_set(
        csvw_metadata_rdf_graph,
        [
            CubeTableIdentifiers(
                "energy-trends-uk-total-energy.csv",
                "energy-trends-uk-total-energy.csv#dataset",
                "energy-trends-uk-total-energy.csv#structure",
            )
        ],
    )

    assert results is not None
    assert len(results) == 1

    result = _get_measure_by_measure_uri(
        results, "energy-trends-uk-total-energy.csv#measure/energy-consumption"
    )
    assert (
        result.measure == "energy-trends-uk-total-energy.csv#measure/energy-consumption"
    )
    assert result.is_pivoted_shape == False


def test_rdf_dependency_loaded() -> None:
    """
    Ensure that the CsvWRdfManager loads dependent RDF graphs to get a complete picture of the cube's metadata.
    """
    dimension_data_file = _test_case_base_dir / "dependencies" / "dimension.csv"
    metadata_file = _test_case_base_dir / "dependencies" / "data.csv-metadata.json"

    csvw_rdf_manager = get_csvw_rdf_manager(metadata_file)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

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
    Ensure that the CsvWRdfManager loads dependent RDF graphs even when there is a cyclic dependency
    """
    metadata_file = _test_case_base_dir / "dependencies" / "cyclic.csv-metadata.json"

    csvw_rdf_manager = get_csvw_rdf_manager(metadata_file)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    # Assert that some RDF has been loaded.
    assert any(csvw_metadata_rdf_graph)


def test_transitive_rdf_dependency_loaded() -> None:
    """
    Ensure that the CsvWRdfManager loads a transitive dependency.
     transitive.csv-metadata.json -> transitive.1.json -> transitive.2.json
    """
    metadata_file = (
        _test_case_base_dir / "dependencies" / "transitive.csv-metadata.json"
    )

    csvw_rdf_manager = get_csvw_rdf_manager(metadata_file)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

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

    csvw_rdf_manager = get_csvw_rdf_manager(metadata_file)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

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


@pytest.mark.vcr
def test_rdf_load_relative_dependencies_only() -> None:
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

    add_triples_for_file_dependencies(
        graph, Path("."), follow_relative_path_dependencies_only=True
    )

    assert (
        URIRef("data.csv#dependency/transitive.2"),
        RDF.type,
        URIRef("http://rdfs.org/ns/void#Dataset"),
    ) not in graph

    assert (
        URIRef("http://example.com/transitive.2"),
        RDFS.label,
        Literal("This is in a transitive dependency"),
    ) not in graph


@pytest.mark.vcr
def test_rdf_load_url_dependency() -> None:
    """
    Test that we can successfully load a URL-based dependency and have transitive relative dependencies work.
    """
    graph = ConjunctiveGraph()
    remote_url = "https://raw.githubusercontent.com/GSS-Cogs/csvcubed/dc1b8df2cd306346e17778cb951417935c91e78b/tests/test-cases/cli/inspect/dependencies/transitive.1.json"

    parse_graph_retain_relative(
        remote_url, format="json-ld", graph=graph.get_context(remote_url)
    )

    # Assert that the dependency is defined in a relative fashion
    assert (
        URIRef("data.csv#dependency/transitive.2"),
        URIRef("http://rdfs.org/ns/void#dataDump"),
        URIRef("transitive.2.json"),
    ) in graph

    # Testing that we can specify a URL as what paths are relative to.
    add_triples_for_file_dependencies(graph, paths_relative_to=remote_url)

    assert (
        URIRef("http://example.com/transitive.2"),
        RDFS.label,
        Literal("This is in a transitive dependency"),
    ) in graph
