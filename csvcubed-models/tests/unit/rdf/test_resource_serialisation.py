from typing import Annotated

import pytest
from rdflib import URIRef, Graph, Literal, RDFS, FOAF, RDF

from csvcubedmodels.rdf.resource import (
    NewResource,
    map_str_to_en_literal,
    map_resource_to_uri,
    Resource,
    ExistingResource,
    InversePredicate,
)
from csvcubedmodels.rdf.triple import Triple, InverseTriple, PropertyStatus


def test_overriding_attribute_annotations():
    """Test that when an annotated property is overridden in a sub-class, the overriding annotation wins out."""

    class A(NewResource):
        p: Annotated[
            str,
            Triple(
                URIRef("http://original-uri"),
                PropertyStatus.mandatory,
                map_str_to_en_literal,
            ),
        ]

    class B(A):
        p: Annotated[
            str,
            Triple(
                URIRef("http://replacement-uri"),
                PropertyStatus.mandatory,
                map_str_to_en_literal,
            ),
        ]

    b = B("http://some-b-uri")
    b.p = "Hello, World"

    graph = b.to_graph(Graph())

    assert len(graph) == 2
    assert (
        URIRef("http://some-b-uri"),
        URIRef("http://replacement-uri"),
        Literal("Hello, World", "en"),
    ) in graph

    assert (
        URIRef("http://some-b-uri"),
        URIRef("http://original-uri"),
        Literal("Hello, World", "en"),
    ) not in graph

    assert (
        URIRef("http://some-b-uri"),
        RDF.type,
        RDFS.Resource,
    ) in graph


def test_resource_serialised_for_new_resource():
    """Ensure that we can use an `NewResource` when providing a `Resource` for serialisation."""

    class A(NewResource):
        p_a: Annotated[
            str,
            Triple(
                URIRef("http://some-predicate-a"),
                PropertyStatus.optional,
                map_str_to_en_literal,
            ),
        ]

    class B(NewResource):
        p_b: Annotated[
            Resource[A],
            Triple(
                URIRef("http://some-predicate-b"),
                PropertyStatus.mandatory,
                map_resource_to_uri,
            ),
        ]

    a = A("http://some-new-resource-a")
    a.p_a = "Hello, World"

    b = B("http://some-new-resource-b")
    b.p_b = a

    graph = b.to_graph(Graph())

    assert (
        URIRef("http://some-new-resource-b"),
        URIRef("http://some-predicate-b"),
        URIRef("http://some-new-resource-a"),
    ) in graph

    # Ensure that we recurviely serialise new resources and their triples.
    assert (
        URIRef("http://some-new-resource-a"),
        URIRef("http://some-predicate-a"),
        Literal("Hello, World", "en"),
    ) in graph


def test_resource_serialised_for_existing_resource():
    """Ensure that we can use an `ExistingResource` inplace of a `NewResource` when providing a `Resource` for
    serialisation."""

    class A(NewResource):
        p_a: Annotated[
            str,
            Triple(
                URIRef("http://some-predicate-a"),
                PropertyStatus.optional,
                map_str_to_en_literal,
            ),
        ]

    class B(NewResource):
        p_b: Annotated[
            Resource[A],
            Triple(
                URIRef("http://some-predicate-b"),
                PropertyStatus.mandatory,
                map_resource_to_uri,
            ),
        ]

    b = B("http://some-new-resource-b")
    b.p_b = ExistingResource("http://some-existing-resource-a")

    graph = b.to_graph(Graph())

    assert (
        URIRef("http://some-new-resource-b"),
        URIRef("http://some-predicate-b"),
        URIRef("http://some-existing-resource-a"),
    ) in graph


def test_resource_serialised_for_circular_reference():
    """
    Ensure that we can correctly serialise graph structures which contain circular references.

    We should *not* get stuck in an infinite loop here.
    """
    a = A_Circular("http://some-new-resource-a")
    b = B_Circular("http://some-new-resource-b")
    a.p_a = b
    b.p_b = a

    graph = b.to_graph(Graph())

    assert (
        URIRef("http://some-new-resource-b"),
        URIRef("http://some-predicate-b"),
        URIRef("http://some-new-resource-a"),
    ) in graph
    assert (
        URIRef("http://some-new-resource-a"),
        URIRef("http://some-predicate-a"),
        URIRef("http://some-new-resource-b"),
    ) in graph


class A_Circular(NewResource):
    p_a: Annotated[
        Resource["B_Circular"],
        Triple(
            URIRef("http://some-predicate-a"),
            PropertyStatus.mandatory,
            map_resource_to_uri,
        ),
    ]


class B_Circular(NewResource):
    p_b: Annotated[
        Resource[A_Circular],
        Triple(
            URIRef("http://some-predicate-b"),
            PropertyStatus.mandatory,
            map_resource_to_uri,
        ),
    ]


def test_multiple_triples_same_attr_serialised():
    """
    Test that we can specify multiple triples against a single attribute and that all of those triples get serialised.
    """

    class A(NewResource):
        p: Annotated[
            str,
            Triple(
                URIRef("http://first-predicate-uri"),
                PropertyStatus.optional,
                map_str_to_en_literal,
            ),
            Triple(
                URIRef("http://second-predicate-uri"),
                PropertyStatus.optional,
                map_str_to_en_literal,
            ),
        ]

    a = A("http://some-uri-a")
    a.p = "Hello, World"
    graph = a.to_graph(Graph())

    assert len(graph) == 3

    assert (
        URIRef("http://some-uri-a"),
        URIRef("http://first-predicate-uri"),
        Literal("Hello, World", "en"),
    ) in graph

    assert (
        URIRef("http://some-uri-a"),
        URIRef("http://second-predicate-uri"),
        Literal("Hello, World", "en"),
    ) in graph

    assert (
        URIRef("http://some-uri-a"),
        RDF.type,
        RDFS.Resource,
    ) in graph


def test_inverse_triple_serialisation():
    """Test that an inverse triple annotation is serialised correctly."""

    class A(NewResource):
        p: Annotated[
            ExistingResource,
            InverseTriple(
                URIRef("http://some-predicate-uri"),
                PropertyStatus.optional,
                map_resource_to_uri,
            ),
        ]

    a = A("http://some-uri-a")
    a.p = ExistingResource("http://some-existing-resource-p")
    graph = a.to_graph(Graph())

    assert len(graph) == 2
    assert (
        URIRef("http://some-existing-resource-p"),
        URIRef("http://some-predicate-uri"),
        URIRef("http://some-uri-a"),
    ) in graph

    assert (
        URIRef("http://some-uri-a"),
        RDF.type,
        RDFS.Resource,
    ) in graph


def test_mandatory_properties_are_required():
    """Test that we get an exception if a mandatory property has not been provided."""

    class A(NewResource):
        p: Annotated[
            str,
            Triple(
                URIRef("http://some-predicate-uri"),
                PropertyStatus.mandatory,
                map_str_to_en_literal,
            ),
        ]

    a = A("http://some-entity-uri")

    with pytest.raises(Exception) as ex:
        a.to_graph(Graph())
    assert "Mandatory RDF property" in str(ex.value)


def test_arbitrary_rdf_triple_serialisation():
    """Test that arbitrary RDF gets serialised properly."""

    class A(NewResource):
        pass

    a = A("http://some-entity-uri")
    a.additional_rdf.add((RDFS.label, Literal("Hello, world.", "en")))
    a.additional_rdf.add(
        (
            InversePredicate(FOAF.primaryTopic),
            URIRef("http://some-resource-with-primary-topic"),
        )
    )

    graph = a.to_graph(Graph())

    assert (
        URIRef("http://some-entity-uri"),
        RDFS.label,
        Literal("Hello, world.", "en"),
    ) in graph
    assert (
        URIRef("http://some-resource-with-primary-topic"),
        FOAF.primaryTopic,
        URIRef("http://some-entity-uri"),
    ) in graph


if __name__ == "__main__":
    pytest.main()
