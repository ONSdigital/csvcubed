import pytest
from typing import Annotated
from rdflib import URIRef, Graph, Literal

from sharedmodels.rdf.resource import NewResource, map_str_to_en_literal, map_resource_to_uri, Resource, ExistingResource
from sharedmodels.rdf.triple import Triple, PropertyStatus

def test_overriding_attribute_annotations():
    """Test that when an annotated property is overridden in a sub-class, the overriding annotation wins out."""

    class A(NewResource):
        p: Annotated[str, Triple(URIRef("http://original-uri"), PropertyStatus.mandatory, map_str_to_en_literal)]

    class B(A):
        p: Annotated[str, Triple(URIRef("http://replacement-uri"), PropertyStatus.mandatory, map_str_to_en_literal)]

    b = B("http://some-b-uri")
    b.p = "Hello, World"

    graph = b.to_graph(Graph())

    assert 1 == len(graph)
    assert (URIRef("http://some-b-uri"), URIRef("http://replacement-uri"), Literal("Hello, World", "en")) in graph
    assert (URIRef("http://some-b-uri"), URIRef("http://original-uri"), Literal("Hello, World", "en")) not in graph

def test_resource_serialised_for_new_resource():
    """Ensure that we can use an `NewResource` when providing a `Resource` for serialisation."""
    class A(NewResource):
        p_a: Annotated[str, Triple(URIRef("http://some-predicate-a"), PropertyStatus.optional, map_str_to_en_literal)]

    class B(NewResource):
        p_b: Annotated[Resource[A], Triple(URIRef("http://some-predicate-b"), PropertyStatus.mandatory, map_resource_to_uri)]

    a = A("http://some-new-resource-a")
    a.p_a = "Hello, World"

    b = B("http://some-new-resource-b")
    b.p_b = a

    graph = b.to_graph(Graph())

    assert (URIRef("http://some-new-resource-b"), URIRef("http://some-predicate-b"), URIRef("http://some-new-resource-a")) in graph

    # Ensure that we recurviely serialise new resources and their triples.
    assert (URIRef("http://some-new-resource-a"), URIRef("http://some-predicate-a"), Literal("Hello, World", "en")) in graph


def test_resource_serialised_for_existing_resource():
    """Ensure that we can use an `ExistingResource` inplace of a `NewResource` when providing a `Resource` for serialisation."""
    class A(NewResource):
        p_a: Annotated[str, Triple(URIRef("http://some-predicate-a"), PropertyStatus.optional, map_str_to_en_literal)]

    class B(NewResource):
        p_b: Annotated[Resource[A], Triple(URIRef("http://some-predicate-b"), PropertyStatus.mandatory, map_resource_to_uri)]

    b = B("http://some-new-resource-b")
    b.p_b = ExistingResource("http://some-existing-resource-a")

    graph = b.to_graph(Graph())

    assert (URIRef("http://some-new-resource-b"), URIRef("http://some-predicate-b"), URIRef("http://some-existing-resource-a")) in graph


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

    assert (URIRef("http://some-new-resource-b"), URIRef("http://some-predicate-b"), URIRef("http://some-new-resource-a")) in graph
    assert (URIRef("http://some-new-resource-a"), URIRef("http://some-predicate-a"), URIRef("http://some-new-resource-b")) in graph


class A_Circular(NewResource):
    p_a: Annotated[Resource["B_Circular"], Triple(URIRef("http://some-predicate-a"), PropertyStatus.mandatory,
                                                  map_resource_to_uri)]


class B_Circular(NewResource):
    p_b: Annotated[
        Resource[A_Circular], Triple(URIRef("http://some-predicate-b"), PropertyStatus.mandatory,
                                     map_resource_to_uri)]


if __name__ == "__main__":
    pytest.main()