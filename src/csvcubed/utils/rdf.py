"""
RDF
---

Utilities to help loading and processing RDF.
"""
from typing import Optional, Tuple, Union

import rdflib
from rdflib.term import Identifier


def parse_graph_retain_relative(
    source=None,
    format: Optional[str] = None,
    location=None,
    file=None,
    data: Optional[Union[str, bytes, bytearray]] = None,
    graph: Optional[rdflib.Graph] = None,
    **args
) -> rdflib.Graph:
    """
    Parse some RDF into an `rdflib.Graph` where relative URIs are retained.
    """
    if graph is None:
        graph = rdflib.Graph()

    graph.parse(
        source=source,
        format=format,
        location=location,
        file=file,
        data=data,
        publicID="http://relative/",
        **args
    )

    _replace_uri_substring_in_graph(graph, "http://relative/", "")

    return graph


def _replace_uri_substring_in_graph(
    csvw_rdf_graph: rdflib.Graph, value_to_replace: str, replacement_value: str
) -> None:
    def replace_uri_in_triple(
        triple: Tuple[Identifier, Identifier, Identifier]
    ) -> Tuple[Identifier, Identifier, Identifier]:
        def replace_uri_in_identifier(identifier: Identifier) -> Identifier:
            if isinstance(identifier, rdflib.URIRef):
                return rdflib.URIRef(
                    str(identifier).replace(value_to_replace, replacement_value)
                )
            else:
                return identifier

        s, p, o = triple
        return (
            replace_uri_in_identifier(s),
            replace_uri_in_identifier(p),
            replace_uri_in_identifier(o),
        )

    triples = [
        replace_uri_in_triple((s, p, o))
        for (s, p, o) in csvw_rdf_graph.triples((None, None, None))
        if isinstance(s, Identifier)
        and isinstance(p, Identifier)
        and isinstance(o, Identifier)
    ]
    csvw_rdf_graph.remove((None, None, None))
    for triple in triples:
        csvw_rdf_graph.add(triple)
