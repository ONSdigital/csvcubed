import pytest
from typing import Dict, Any
from rdflib import RDFS, Literal, URIRef, Graph

from csvcubed.models.cube import *
from csvcubed.models.cube import NewQbConcept
from csvcubed.models.cube.qb.components.arbitraryrdf import (
    RdfSerialisationHint,
    TripleFragment,
)
from csvcubed.models.cube.uristyle import URIStyle
from csvcubed.writers.skoscodelistwriter import SkosCodeListWriter


basic_code_list = NewQbCodeList(
    CatalogMetadata("Some CodeList"),
    [
        NewQbConcept(
            "First Concept",
            code="1st-20%concept",
            description="This is the first concept.",
        ),
        NewQbConcept("Second%20 Concept", parent_code="1st-20%concept", sort_order=20),
    ],
)

parent_uri_identifier_override_code_list = NewQbCodeList(
    CatalogMetadata("Some CodeList"),
    [
        NewQbConcept(
            "First Concept",
            code="1st-concept",
            description="This is the first concept.",
            uri_safe_identifier_override="1st-20%concept",
        ),
        NewQbConcept("Second%20 Concept", parent_code="1st-concept", sort_order=20),
    ],
)


def test_csvw_metadata_url_withoutFileExtension_style():
    """
    Test that the generated URL for a CSVW still contains file endings even when configured to use without file extension URI style
    """
    code_list_withoutFileExtensions_uri_style = NewQbCodeList(
        CatalogMetadata("Some CodeList"), [], uri_style=URIStyle.WithoutFileExtensions
    )
    writer = SkosCodeListWriter(code_list_withoutFileExtensions_uri_style)
    data = writer._get_csvw_metadata()
    actual_url = data["url"]
    assert actual_url == "some-codelist.csv"


def test_code_list_data_mapping():
    """
    Test that a `pd.DataFrame` containing the codes is correctly generated from a `NewQbCodeList`.
    """
    writer = SkosCodeListWriter(basic_code_list)
    data = writer._get_code_list_data()
    actual_column_names = {str(c) for c in data.columns}
    assert {
        "Uri Identifier",
        "Label",
        "Notation",
        "Parent Uri Identifier",
        "Sort Priority",
        "Description",
    } == actual_column_names

    first_concept: Dict[str, Any] = data.iloc[[0]].to_dict("records")[0]
    assert first_concept["Uri Identifier"] == "1st-20-concept"
    assert first_concept["Label"] == "First Concept"
    assert first_concept["Notation"] == "1st-20%concept"
    assert first_concept.get("Parent Uri Identifier") is None
    assert first_concept["Sort Priority"] == 0
    assert first_concept["Description"] == "This is the first concept."

    second_concept: Dict[str, Any] = data.iloc[[1]].to_dict("records")[0]
    assert second_concept["Uri Identifier"] == "second-20-concept"
    assert second_concept["Label"] == "Second%20 Concept"
    assert second_concept["Notation"] == "second-20-concept"
    assert second_concept["Parent Uri Identifier"] == "1st-20-concept"
    assert second_concept["Sort Priority"] == 20
    assert second_concept.get("Description") is None


def test_code_list_data_mapping_for_parent_defined_with_uri_safe_id():
    """
    Test that a `pd.DataFrame` containing the codes is correctly generated from a `NewQbCodeList` for a concept in which the parent is defined with the uri safe identifier.
    """
    writer = SkosCodeListWriter(parent_uri_identifier_override_code_list)
    data = writer._get_code_list_data()
    actual_column_names = {str(c) for c in data.columns}
    assert {
        "Uri Identifier",
        "Label",
        "Notation",
        "Parent Uri Identifier",
        "Sort Priority",
        "Description",
    } == actual_column_names

    first_concept: Dict[str, Any] = data.iloc[[0]].to_dict("records")[0]
    assert first_concept["Uri Identifier"] == "1st-20%concept"
    assert first_concept["Label"] == "First Concept"
    assert first_concept["Notation"] == "1st-concept"
    assert first_concept.get("Parent Uri Identifier") is None
    assert first_concept["Sort Priority"] == 0
    assert first_concept["Description"] == "This is the first concept."

    second_concept: Dict[str, Any] = data.iloc[[1]].to_dict("records")[0]
    assert second_concept["Uri Identifier"] == "second-20-concept"
    assert second_concept["Label"] == "Second%20 Concept"
    assert second_concept["Notation"] == "second-20-concept"
    assert second_concept["Parent Uri Identifier"] == "1st-20%concept"
    assert second_concept["Sort Priority"] == 20
    assert second_concept.get("Description") is None


def test_arbitrary_rdf_serialisation_new_code_list():
    """
    Test that when arbitrary RDF is specified against a new code list, it is serialised correctly.
    """
    code_list = NewQbCodeList(
        CatalogMetadata("Some Code List"),
        concepts=[NewQbConcept("A"), NewQbConcept("B")],
        arbitrary_rdf=[
            TripleFragment(RDFS.label, "Some code list label"),
            TripleFragment(
                RDFS.label,
                "Some dcat dataset label",
                RdfSerialisationHint.CatalogDataset,
            ),
        ],
    )
    skos_writer = SkosCodeListWriter(code_list)
    dataset = skos_writer._get_catalog_metadata("http://some-scheme-uri")
    graph = dataset.to_graph(Graph())

    assert (
        URIRef("http://some-scheme-uri"),
        RDFS.label,
        Literal("Some code list label"),
    ) in graph

    assert (
        URIRef("http://some-scheme-uri"),
        RDFS.label,
        Literal("Some dcat dataset label"),
    ) in graph


if __name__ == "__main__":
    pytest.main()
