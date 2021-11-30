"""
Resources
---------
"""
from abc import ABC
from collections.abc import Iterable
from typing import (
    Annotated,
    List,
    get_type_hints,
    get_args,
    Set,
    Any,
    TypeVar,
    Union,
    Optional,
    Tuple,
    Callable,
)

import rdflib
from rdflib import URIRef, Graph
from rdflib.term import Literal, Identifier

from .datatypes import MARKDOWN
from .triple import AbstractTriple, Triple, PropertyStatus
from csvcubedmodels.rdf.namespaces import RDF, RDFS


class RdfResource(ABC):
    uri: URIRef

    def __init__(self, uri: str):
        self.uri = URIRef(uri)


class ExistingResource(RdfResource):
    """Node - represents an existing node which we don't want to redefine. Just specify its URI."""

    def __init__(self, uri: str):
        RdfResource.__init__(self, uri)


class ExistingResourceWithLiteral(ExistingResource):
    """Due to the way we intend to allow for existing resources which are literals, we need a range here."""

    range: Union[RdfResource, ExistingResource]


class InversePredicate(URIRef):
    """An rdflib identifier which represents a predicate where the subject/object are reversed."""

    ...


RdfResourceType = TypeVar("RdfResourceType", covariant=True)
Resource = Union[RdfResourceType, ExistingResource]
"""Represents an RdfResource OR an ExistingNode"""

MaybeResource = Union[RdfResourceType, ExistingResource, None]
"""Represents an RdfResource OR an ExistingNode OR None"""


class NewResource(RdfResource, ABC):
    rdf_types: Set[URIRef]
    additional_rdf: Set[Tuple[Identifier, Identifier]]
    """A place for arbitrary RDF attached to this subject/entity."""

    def __init__(self, uri: str):
        RdfResource.__init__(self, uri)
        # Multiple-inheritance safeguard
        self.rdf_types = getattr(self, "rdf_types", {RDFS.Resource})
        # Multiple-inheritance safeguard
        self.additional_rdf = getattr(self, "additional_rdf", set())

    @property
    def uri_str(self) -> str:
        return str(self.uri)

    @uri_str.setter
    def uri_str(self, uri: str):
        self.uri = URIRef(uri)

    def to_graph(
        self, graph: rdflib.Graph, objects_already_processed: Set[object] = set()
    ) -> rdflib.Graph:
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

        type_hints = self._get_type_hints()

        for property_key, typing_hint in type_hints.items():
            property_value = getattr(self, property_key, None)
            type_hints = get_args(typing_hint)
            triple_mappings: List[AbstractTriple] = [
                th for th in type_hints if isinstance(th, AbstractTriple)
            ]
            for triple in triple_mappings:
                # Ensure we can cope with one-to-many relationships
                self._add_triples_to_graph(
                    graph,
                    property_key,
                    property_value,
                    triple,
                    objects_already_processed,
                )

        for (key, value) in self.additional_rdf:
            # Add arbitrary RDF to the graph.
            if isinstance(key, InversePredicate):
                graph.add((value, URIRef(str(key)), self.uri))
            else:
                graph.add((self.uri, key, value))

        return graph

    def _get_type_hints(self) -> dict:
        """
        Fetches type hints associated with this class.

        Ensures that overridden properties have their type hints overridden too.
        """

        type_hints = {}
        for c in reversed(self.__class__.mro()):
            type_hints = dict(type_hints, **get_type_hints(c, include_extras=True))

        return type_hints

    def _add_triples_to_graph(
        self,
        graph: Graph,
        property_key: str,
        property_value: Any,
        triple: AbstractTriple,
        objects_already_processed: Set[object],
    ):
        value_is_iterable = isinstance(property_value, Iterable) and not isinstance(
            property_value, str
        )
        if value_is_iterable:
            all_values = list(property_value)
            value_is_empty_iterable = len(all_values) == 0
        else:
            value_is_empty_iterable = False
            all_values = [property_value]

        property_value_is_empty = (
            property_value is None or property_value == "" or value_is_empty_iterable
        )

        if property_value_is_empty:
            if triple.status == PropertyStatus.mandatory:
                raise Exception(
                    f"Mandatory RDF property '{triple.predicate}' "
                    + f"({type(self).__name__}.{property_key}) has not been provided."
                )
        else:
            try:
                for val in all_values:
                    triple.add_to_graph(graph, self.uri, val)

                    # If this resource links to another one, then we should make sure that is serialised too.
                    if isinstance(val, NewResource):
                        val.to_graph(graph, objects_already_processed)

            except Exception as e:
                raise Exception(
                    f"Error adding RDF property '{triple.predicate}' "
                    f" ({type(self).__name__}.{property_key})."
                ) from e


def map_str_to_en_literal(s: str) -> Literal:
    return Literal(s, "en")


def map_resource_to_uri(entity: RdfResource) -> URIRef:
    return entity.uri


def map_to_literal_with_datatype(datatype: URIRef) -> Callable[[Any], Literal]:
    return lambda val: Literal(val, datatype=datatype)


def map_str_to_markdown(s: str) -> Literal:
    return Literal(s, MARKDOWN)


class NewResourceWithLabel(NewResource, ABC):
    label: Annotated[
        str, Triple(RDFS.label, PropertyStatus.mandatory, map_str_to_en_literal)
    ]


class NewMetadataResource(NewResourceWithLabel, ABC):
    comment: Annotated[
        Optional[str],
        Triple(RDFS.comment, PropertyStatus.recommended, map_str_to_en_literal),
    ]


def maybe_existing_resource(
    maybe_resource_uri: Optional[str],
) -> Optional[ExistingResource]:
    if maybe_resource_uri is None:
        return None

    return ExistingResource(maybe_resource_uri)
