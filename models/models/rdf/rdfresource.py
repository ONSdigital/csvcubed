import rdflib
from rdflib import URIRef
from rdflib.term import Literal
from typing import Annotated, List, get_type_hints, get_args
from abc import ABC
from rdflib import RDFS, RDF

from .rdfpropertymap import RdfPropertyMap, PropertyStatus


class RdfResource(ABC):
    uri: URIRef
    _rdf_types: List[URIRef]

    def __init__(self, uri: str, rdf_types: List[URIRef]):
        self.uri = URIRef(uri)
        self._rdf_types = rdf_types

    @property
    def uri_str(self) -> str:
        return str(self.uri)

    @uri_str.setter
    def uri_str(self, uri: str):
        self.uri = URIRef(uri)

    def to_graph(self, graph: rdflib.Graph) -> rdflib.Graph:
        """
        Serialises the current object into a new RDF Graph.

        Raises an exception where properties marked as RdfPropertyStatus.mandatory have not been provided.
        """
        for rdf_type in self._rdf_types:
            graph.add((self.uri, RDF.type, rdf_type))

        """
        The following code depends on all RDF properties being defined using the typing.Annotation class.
        e.g. `label: Annotated[str, RdfPropertyMap(RDFS.label, RdfPropertyStatus.mandatory, map_str_to_en_literal)]`
        """

        type_hints_list_of_lists = [get_type_hints(c, include_extras=True).items() for c in self.__class__.mro()]
        type_hints = [th for th_list in type_hints_list_of_lists for th in th_list]
        for property_key, typing_hint in type_hints:
            property_value = getattr(self, property_key, None)
            type_hints = get_args(typing_hint)
            rdf_mappings: List[RdfPropertyMap] = [th for th in type_hints if isinstance(th, RdfPropertyMap)]
            for mapping in rdf_mappings:
                property_value_is_empty = property_value is None or property_value == ""
                if mapping.status == PropertyStatus.mandatory and property_value_is_empty:
                    raise Exception(f"Mandatory RDF property '{mapping.predicate}' " +
                                    f"({type(self).__name__}.{property_key}) has not been provided.")
                if not property_value_is_empty:
                    mapped_value = mapping.map_to_rdf_literal(property_value)
                    graph.add((self.uri, mapping.predicate, mapped_value))

            # If this resource links to another one, then we should make sure that is serialised too.
            if isinstance(property_value, RdfResource):
                property_value.to_graph(graph)

        return graph


def map_str_to_en_literal(s: str) -> str:
    return Literal(s, 'en')


def map_entity_to_uri(entity: RdfResource) -> URIRef:
    return entity.uri


class RdfMetadataResource(RdfResource, ABC):
    label: Annotated[str, RdfPropertyMap(RDFS.label, PropertyStatus.mandatory, map_str_to_en_literal)]
    comment: Annotated[str, RdfPropertyMap(RDFS.comment, PropertyStatus.mandatory, map_str_to_en_literal)]



