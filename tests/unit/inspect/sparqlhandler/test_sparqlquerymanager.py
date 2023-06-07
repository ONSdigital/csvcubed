from pathlib import Path

import pytest
from rdflib import DCAT, RDF, RDFS, ConjunctiveGraph, Graph, Literal, URIRef

from csvcubed.inspect.sparql_handler.sparqlquerymanager import (
    select_csvw_table_schema_file_dependencies,
    select_metadata_dependencies,
)
from csvcubed.inspect.tableschema import add_triples_for_file_dependencies
from csvcubed.models.inspect.sparqlresults import MetadataDependenciesResult
from csvcubed.utils.rdf import parse_graph_retain_relative
from tests.helpers.repository_cache import (
    get_code_list_repository,
    get_csvw_rdf_manager,
    get_data_cube_repository,
)
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"
_csvw_test_cases_dir = get_test_cases_dir() / "utils" / "csvw"


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
