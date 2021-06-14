import rdflib
from rdflib import URIRef
from rdflib.term import Literal
from typing import Annotated, List, get_type_hints, get_args, Set
from abc import ABC
from rdflib import RDFS, RDF

from .triple import AbstractTriple, Triple, PropertyStatus


MARKDOWN = URIRef('https://www.w3.org/ns/iana/media-types/text/markdown#Resource')


class RdfResource(ABC):
    uri: URIRef
    rdf_types: Set[URIRef]

    def __init__(self, uri: str):
        self.uri = URIRef(uri)
        self.rdf_types = set()

    @property
    def uri_str(self) -> str:
        return str(self.uri)

    @uri_str.setter
    def uri_str(self, uri: str):
        self.uri = URIRef(uri)

    def to_graph(self, graph: rdflib.Graph, objects_already_processed: Set[object] = set()) -> rdflib.Graph:
        """
        Serialises the current object into a new RDF Graph.

        Raises an exception where properties marked as RdfPropertyStatus.mandatory have not been provided.
        """
        if self in objects_already_processed:
            # Cyclic reference, we have already processed this object.
            return

        objects_already_processed.add(self)

        for rdf_type in self.rdf_types:
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
            triple_mappings: List[AbstractTriple] = [th for th in type_hints if isinstance(th, AbstractTriple)]
            for triple in triple_mappings:
                property_value_is_empty = property_value is None or property_value == ""
                if triple.status == PropertyStatus.mandatory and property_value_is_empty:
                    raise Exception(f"Mandatory RDF property '{triple.predicate}' " +
                                    f"({type(self).__name__}.{property_key}) has not been provided.")
                if not property_value_is_empty:
                    try:
                        triple.add_to_graph(graph, self.uri, property_value)
                    except Exception as e:
                        raise Exception(f"Error adding RDF property '{triple.predicate}' "
                                        f" ({type(self).__name__}.{property_key}).") from e

            # If this resource links to another one, then we should make sure that is serialised too.
            if isinstance(property_value, RdfResource):
                property_value.to_graph(graph, objects_already_processed)

        return graph


def map_str_to_en_literal(s: str) -> Literal:
    return Literal(s, 'en')


def map_entity_to_uri(entity: RdfResource) -> URIRef:
    return entity.uri


def map_str_to_markdown(s: str) -> Literal:
    return Literal(s, MARKDOWN)


class RdfMetadataResource(RdfResource, ABC):
    label: Annotated[str, Triple(RDFS.label, PropertyStatus.mandatory, map_str_to_en_literal)]
    comment: Annotated[str, Triple(RDFS.comment, PropertyStatus.mandatory, map_str_to_en_literal)]



