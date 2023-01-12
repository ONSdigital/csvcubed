"""
SPARQL
------

Utilities to help when running SPARQL queries.
"""
import os.path
from pathlib import Path, PosixPath
from typing import Any, Callable, Dict, List, Optional, Union

import rdflib.term
from rdflib import Graph, Literal
from rdflib.query import ResultRow
from rdflib.term import Node

from csvcubed.models.csvcubedexception import (
    UnexpectedSparqlAskQueryResponseTypeException,
    UnexpectedSparqlAskQueryResultsException,
)
from csvcubed.models.sparql.valuesbinding import ValuesBinding


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


def select(
    query: str,
    graph: Graph,
    init_bindings: Optional[Dict[str, Node]] = None,
    values_bindings: List[ValuesBinding] = [],
) -> List[ResultRow]:
    """
    Executes the given SELECT query on the rdf graph.

    Member of :file:`./sparql.py`.

    :return: `List[ResultRow]` - List containing the results.

    """
    if any(values_bindings):
        # We should be able to just add the `VALUES` on after the query, but this falls down when done in combination
        # with a `GROUP BY` due to a bug in rdflib (https://github.com/RDFLib/rdflib/pull/2188).
        # So, until that is merged in and released, we'll have to insert these `VALUES` within the query.
        # todo: Undo this once https://github.com/RDFLib/rdflib/pull/2188 is merged and complete.
        # query += _convert_values_bindings_to_sparql(values_bindings)
        last_closing_brace_index = query.rindex("}")
        query = (
            query[0:last_closing_brace_index]
            + "\n"
            + _convert_values_bindings_to_sparql(values_bindings)
            + "\n"
            + query[last_closing_brace_index:]
        )

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


def _convert_values_bindings_to_sparql(values_bindings: List[ValuesBinding]) -> str:
    """
    A little hack to add support for init bindings with lists of parameters.
    """
    bindings_sparql = ""

    for binding in values_bindings:
        keys = " ".join(f"?{k}" for k in binding.variable_names)

        def _gen_values_row(
            row: List[Union[rdflib.term.URIRef, rdflib.term.BNode, rdflib.term.Literal]]
        ) -> str:
            return " ".join(v.n3() for v in row)

        values = "\n".join(f"( {_gen_values_row(r)} )" for r in binding.rows)
        bindings_sparql += f"\n VALUES ( {keys} ) \n {{ \n {values} \n }}"
    return bindings_sparql


def path_to_file_uri_for_rdflib(file: Path) -> str:
    """
    Converts a `pathlib.Path` into a file:///.... URI.

    This is necessary due to windows paths being altered by rdflib when they're loaded.
    """

    file_uri_prefix = "file://" if isinstance(file, PosixPath) else "file:///"

    return file_uri_prefix + os.path.normpath(str(file.absolute())).replace("\\", "/")
