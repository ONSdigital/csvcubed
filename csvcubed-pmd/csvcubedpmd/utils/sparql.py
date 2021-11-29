"""
SPARQL
------

Utilities to help when running SPARQL queries.
"""
from rdflib import Graph


def ask(query: str, graph: Graph) -> bool:
    results = list(graph.query(query))

    if len(results) == 1:
        result = results[0]
        if isinstance(result, bool):
            return result
        else:
            raise Exception(f"Unexpected ASK query response type {type(result)}")
    else:
        raise Exception(f"Unexpected number of results for ASK query {len(results)}.")
