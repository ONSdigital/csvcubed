"""
Find Where
----------

Allows you to find CSV-W metadata files in a directory (or sub-directories) which match a given SPARQL ASK
Query.
"""
from pathlib import Path
from rdflib import Graph
from typing import List

from csvcubedpmd.utils.sparql import ask


def find_where(find_location: Path, ask_query: str, negate: bool) -> None:
    """
    Find all CSV-Ws inside a directory which match the provided :obj:`ask_query`.
    """
    matching_csvws: List[Path] = []
    for csvw_metadata_file in find_location.rglob("**/*csv-metadata.json"):
        graph_data = Graph()
        graph_data.load(str(csvw_metadata_file), format="json-ld")
        if ask(ask_query, graph_data) != negate:
            matching_csvws.append(csvw_metadata_file)

    for matching_csvw_path in matching_csvws:
        print(str(matching_csvw_path))
