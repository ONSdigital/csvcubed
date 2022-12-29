"""
Values Binding
--------------

Holds the ValuesBinding model which allows binding lists of values to variables within SPARQL queries.
"""
from dataclasses import dataclass
from typing import List, Union

import rdflib.term


@dataclass
class ValuesBinding:
    """Allows binding lists of values to variables within SPARQL queries."""

    variable_names: List[str]
    rows: List[List[Union[rdflib.term.URIRef, rdflib.term.BNode, rdflib.term.Literal]]]
