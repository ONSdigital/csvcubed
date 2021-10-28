import json

import pytest
from typing import Dict, Any
from rdflib import RDFS, Literal, URIRef, Graph

from csvcubed.models.cube import *
from csvcubed.models.cube.qb.components.arbitraryrdf import (
    RdfSerialisationHint,
    TripleFragment,
)
from csvcubed.writers.skoscodelistwriter import SkosCodeListWriter


basic_code_list = NewQbCodeList(
    CatalogMetadata("Some CodeList"),
    [
        NewQbConcept(
            "First Concept",
            code="1st-concept",
            description="This is the first concept.",
        ),
        NewQbConcept("Second Concept", parent_code="1st-concept", sort_order=20),
    ],
)


def test_code_list_data_mapping():
    """
    Test that a `pd.DataFrame` containing the codes is correctly generated from a `NewQbCodeList`.
    """
    writer = SkosCodeListWriter(basic_code_list)
    data = writer._get_code_list_data()
    actual_column_names = {str(c) for c in data.columns}
    assert {
        "Label",
        "Notation",
        "Parent Notation",
        "Sort Priority",
        "Description",
    } == actual_column_names

    first_concept: Dict[str, Any] = data.iloc[[0]].to_dict("records")[0]
    assert first_concept["Label"] == "First Concept"
    assert first_concept["Notation"] == "1st-concept"
    assert first_concept.get("Parent Notation") is None
    assert first_concept["Sort Priority"] == 0
    assert first_concept["Description"] == "This is the first concept."

    second_concept: Dict[str, Any] = data.iloc[[1]].to_dict("records")[0]
    assert second_concept["Label"] == "Second Concept"
    assert second_concept["Notation"] == "second-concept"
    assert second_concept["Parent Notation"] == "1st-concept"
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
