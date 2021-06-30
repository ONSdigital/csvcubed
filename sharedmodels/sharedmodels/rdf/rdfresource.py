import rdflib
from rdflib import URIRef, Graph, RDFS, RDF
from rdflib.term import Literal, Identifier
from typing import Annotated, List, get_type_hints, get_args, Set, Any, Dict, TypeVar, Union, Optional
from abc import ABC
from collections.abc import Iterable


from .triple import AbstractTriple, Triple, PropertyStatus
from .datatypes import MARKDOWN


class RdfResource(ABC):
    uri: URIRef
    rdf_types: Set[URIRef]
    additional_rdf: Dict[Identifier, Identifier]
    """A place for arbitrary RDF attached to this subject/entity."""

    def __init__(self, uri: str):
        self.uri = URIRef(uri)
        self.rdf_types = set()
        self.additional_rdf = {}

    @property
    def uri_str(self) -> str:
        return str(self.uri)

    @uri_str.setter
    def uri_str(self, uri: str):
        self.uri = URIRef(uri)

    def to_graph(self, graph: rdflib.Graph, objects_already_processed: Set[object] = set()) -> rdflib.Graph:
        """
        Serialises the current object into an RDF Graph.

        Raises an exception where properties marked as PropertyStatus.mandatory have not been provided.
        """
        if self in objects_already_processed:
            # Cyclic reference, we have already processed this object.
            return graph

        objects_already_processed.add(self)

        for rdf_type in self.rdf_types:
            graph.add((self.uri, RDF.type, rdf_type))

        """
        The following code depends on all RDF properties being defined using the typing.Annotation class.
        e.g. `label: Annotated[str, Triple(RDFS.label, PropertyStatus.mandatory, map_str_to_en_literal)]`
        """

        type_hints_list_of_lists = [get_type_hints(c, include_extras=True).items() for c in self.__class__.mro()]
        type_hints = [th for th_list in type_hints_list_of_lists for th in th_list]
        for property_key, typing_hint in type_hints:
            property_value = getattr(self, property_key, None)
            type_hints = get_args(typing_hint)
            triple_mappings: List[AbstractTriple] = [th for th in type_hints if isinstance(th, AbstractTriple)]
            for triple in triple_mappings:
                # Ensure we can cope with one-to-many relationships
                self._add_triple_to_graph(graph, property_key, property_value, triple, objects_already_processed)

        for (key, value) in self.additional_rdf.items():
            # Add arbitrary RDF to the graph.
            graph.add((self.uri, key, value))

        return graph

    def _add_triple_to_graph(self, graph: Graph, property_key: str, property_value: Any, triple: AbstractTriple,
                             objects_already_processed: Set[object]):
        value_is_iterable = isinstance(property_value, Iterable) and not isinstance(property_value, str)
        if value_is_iterable:
            all_values = list(property_value)
            value_is_empty_iterable = len(all_values) == 0
        else:
            value_is_empty_iterable = False
            all_values = [property_value]

        property_value_is_empty = property_value is None or property_value == "" or value_is_empty_iterable

        if property_value_is_empty:
            if triple.status == PropertyStatus.mandatory:
                raise Exception(f"Mandatory RDF property '{triple.predicate}' " +
                                f"({type(self).__name__}.{property_key}) has not been provided.")
        else:
            try:
                for val in all_values:
                    triple.add_to_graph(graph, self.uri, val)

                    # If this resource links to another one, then we should make sure that is serialised too.
                    if isinstance(val, RdfResource):
                        val.to_graph(graph, objects_already_processed)

            except Exception as e:
                raise Exception(f"Error adding RDF property '{triple.predicate}' "
                                f" ({type(self).__name__}.{property_key}).") from e


def map_str_to_en_literal(s: str) -> Literal:
    return Literal(s, 'en')


def map_resource_to_uri(entity: RdfResource) -> URIRef:
    return entity.uri


def map_str_to_markdown(s: str) -> Literal:
    return Literal(s, MARKDOWN)


class RdfMetadataResource(RdfResource, ABC):
    label: Annotated[str, Triple(RDFS.label, PropertyStatus.mandatory, map_str_to_en_literal)]
    comment: Annotated[str, Triple(RDFS.comment, PropertyStatus.mandatory, map_str_to_en_literal)]


class ExistingResource(RdfResource):
    """Node - represents an existing node which we don't want to redefine. Just specify its URI."""
    def __init__(self, uri: str):
        RdfResource.__init__(self, uri)


def maybe_existing(uri: Optional[str]) -> Optional[ExistingResource]:
    if uri is None:
        return None

    return ExistingResource(uri)


RdfResourceType = TypeVar("RdfResourceType", covariant=True)
Resource = Union[RdfResourceType, ExistingResource]
"""Represents an RdfResource OR an ExistingNode"""

MaybeEntity = Optional[Union[RdfResourceType, ExistingResource]]
"""Represents an RdfResource OR an ExistingNode OR None"""
