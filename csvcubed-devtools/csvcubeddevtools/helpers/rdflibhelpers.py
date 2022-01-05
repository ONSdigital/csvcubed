"""
RDF-Lib Utilities
-----------------

Utilities to help when working with rdflib.
"""
from rdflib import Graph


def serialise_to_string(graph: Graph, format: str = "turtle") -> str:
    """
    Safely serialise an :class:`rdflib.Graph` to a string without worrying about differences between
    rdflib 5.0.0 and 6.0.0.
    """

    result = graph.serialize(format=format)
    if isinstance(result, bytes):
        return result.decode("utf-8")
    elif isinstance(result, str):
        return result
    else:
        raise Exception(f"Unexpected serialised value type {type(result)}.")
