"""
Triples (serialisation)
-----------------------
"""
from typing import Callable, Any
from abc import ABC, abstractmethod

from rdflib import  URIRef, Graph
from rdflib.term import Identifier
from enum import Enum


class PropertyStatus(Enum):
    optional = 0
    mandatory = 1
    recommended = 2


class AbstractTriple(ABC):
    predicate: URIRef
    status: PropertyStatus

    def __init__(self, predicate: URIRef, status: PropertyStatus):
        self.predicate = predicate
        self.status = status

    @abstractmethod
    def add_to_graph(self, graph: Graph, entity_uri: URIRef, value: Any):
        pass


class Triple(AbstractTriple):
    """
        Class representing the triple `<entity_uri> <predicate> <property_mapper(property_value)>`.
    """

    map_to_rdf: Callable[[Any], Identifier]
    """Maps the python value to an RDF Literal for serialisation."""

    def __init__(self, predicate: URIRef, status: PropertyStatus, property_mapper: Callable[[Any], Identifier]):
        """
        Class representing the triple `<entity_uri> <predicate> <property_mapper(property_value)>`.

        :param predicate:
        :param status:
        :param property_mapper:
        """
        AbstractTriple.__init__(self, predicate, status)
        self.map_to_rdf = property_mapper

    def add_to_graph(self, graph: Graph, entity_uri: URIRef, value: Any):
        mapped_value = self.map_to_rdf(value)
        graph.add((entity_uri, self.predicate, mapped_value))


class InverseTriple(AbstractTriple):
    """
        Class representing the triple `<property_to_uri_mapper(property_value)> <predicate> <entity_uri>`.
    """

    map_to_uri: Callable[[Any], URIRef]
    """Maps the python value to an RDF Literal for serialisation."""

    def __init__(self, predicate: URIRef, status: PropertyStatus, property_to_uri_mapper: Callable[[Any], URIRef]):
        """
        Class representing the triple `<property_to_uri_mapper(property_value)> <predicate> <entity_uri>`.

        :param predicate:
        :param status:
        :param property_mapper:
        """
        AbstractTriple.__init__(self, predicate, status)
        self.map_to_uri = property_to_uri_mapper

    def add_to_graph(self, graph: Graph, entity_uri: URIRef, value: Any):
        mapped_value = self.map_to_uri(value)
        graph.add((mapped_value, self.predicate, entity_uri))

