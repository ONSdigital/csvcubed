from typing import Callable, Any
from rdflib import Literal, URIRef
from enum import Enum

MappingFunction = Callable[[Any], Literal]


class PropertyStatus(Enum):
    optional = 0
    mandatory = 1
    recommended = 2


class RdfPropertyMap:
    predicate: URIRef
    status: PropertyStatus
    map_to_rdf_literal: MappingFunction
    """Maps the python value to an RDF Literal for serialisation."""

    def __init__(self, predicate: URIRef, status: PropertyStatus, map_to_rdf_literal: MappingFunction):
        self.predicate = predicate
        self.status = status
        self.map_to_rdf_literal = map_to_rdf_literal
