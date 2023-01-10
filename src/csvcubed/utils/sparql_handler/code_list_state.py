from dataclasses import dataclass

import rdflib


@dataclass
class CodeListState:
    rdf_graph: rdflib.Graph
