import pytest
from typing import Annotated
from rdflib import URIRef, Graph, Literal

from sharedmodels.rdf.resource import NewResource, map_str_to_en_literal
from sharedmodels.rdf.triple import Triple, PropertyStatus


def ask(g: Graph, ask_query: str) -> bool:
    results = g.query(ask_query)
    return bool(results)


def test_something():
    class A(NewResource):
        p: Annotated[str, Triple(URIRef("http://original-uri"), PropertyStatus.mandatory, map_str_to_en_literal)]

    class B(A):
        p: Annotated[str, Triple(URIRef("http://replacement-uri"), PropertyStatus.mandatory, map_str_to_en_literal)]

    b = B("http://some-b-uri")
    b.p = "Hello, World"

    graph: Graph = Graph()
    b.to_graph(graph)
    # assert 1 == len(graph)
    assert (URIRef("http://some-b-uri"), URIRef("http://replacement-uri"), Literal("Hello, World", "en")) in graph
    assert (URIRef("http://some-b-uri"), URIRef("http://original-uri"), Literal("Hello, World", "en")) not in graph



if __name__ == "__main__":
    pytest.main()