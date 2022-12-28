"""
Values Binding
--------------

Holds the ValuesBinding model which allows binding lists of values to variables within SPARQL queries.
"""
from dataclasses import dataclass
from typing import List

import rdflib.term


@dataclass
class ValuesBinding:
    """Allows binding lists of values to variables within SPARQL queries."""

    variable_names: List[str]
    rows: List[List[rdflib.term.Node]]
