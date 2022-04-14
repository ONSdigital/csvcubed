"""
SPARQL
------

Utilities to help when running SPARQL queries.
"""
from pathlib import Path
from typing import List, Optional, Any, Callable

from rdflib import Graph, Literal
from rdflib.query import ResultRow

from csvcubed.models.csvcubedexception import (
    UnexpectedSparqlAskQueryResponseTypeException,
    UnexpectedSparqlAskQueryResultsException,
)


def none_or_map(val: Optional[Any], map_func: Callable[[Any], Any]) -> Optional[Any]:
    if val is None:
        return None
    else:
        return map_func(val)


def ask(query_name: str, query: str, graph: Graph) -> bool:
    """
    Executes the given ASK query on the rdf graph.

    Member of :file:`./sparql.py`.

    :return: `bool` - Whether the given query yeilds true or false
    """
    results = list(graph.query(query))

    if len(results) == 1:
        result = results[0]
        if isinstance(result, bool):
            return result
        else:
            raise UnexpectedSparqlAskQueryResponseTypeException(
                query_name, type(result)
            )
    else:
        raise UnexpectedSparqlAskQueryResultsException(query_name, len(results))


def select(query: str, graph: Graph, init_bindings=None) -> List[ResultRow]:
    """
    Executes the given SELECT query on the rdf graph.

    Member of :file:`./sparql.py`.

    :return: `List[ResultRow]` - List containing the results.

    """
    results: List[ResultRow] = [
        result
        for result in graph.query(query, initBindings=init_bindings)
        if isinstance(result, ResultRow)
        and isinstance(result.labels, dict)
        and any(
            [
                result[key] is not None and result[key] != Literal("")
                for key in result.labels.keys()
            ]
        )
    ]
    return results


def path_to_file_uri_for_rdflib(file: Path) -> str:
    """
    Converts a `pathlib.Path` into a file:///.... URI.

    This is necessary due to windows paths being altered by rdflib when they're loaded.
    """
    return "file://" + str(file).replace("\\", "/")
