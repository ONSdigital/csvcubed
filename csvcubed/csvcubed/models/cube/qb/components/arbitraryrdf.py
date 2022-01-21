"""
Arbitrary RDF Container
-----------------------

Defines a mixin permitting arbitrary RDF to be added to a qb component.
"""
from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass
from enum import Enum
from typing import Set, Dict, Union, List, Tuple
from rdflib.term import Identifier, URIRef, Literal
from csvcubedmodels.rdf import NewResource, InversePredicate

from csvcubed.models.pydanticmodel import PydanticModel
from csvcubed.utils.uri import looks_like_uri


class RdfSerialisationHint(Enum):
    """
    Provides a hint as to which RDF resource to serialise the triple fragment against.
    """

    DefaultNode = 0
    """The primary RDF node that the class generates."""

    Component = 1
    """The `qb:ComponentSpecification` that the class generates."""

    Property = 2
    """The `rdf:Property` that the class generates."""

    AttributeValue = 3
    """The attribute value that the class generates."""

    ConceptScheme = 4
    """The `skos:ConceptScheme` that the class generates."""

    CatalogDataset = 5
    """The `dcat:Dataset` that the class generates."""

    Unit = 6
    """The unit that the class generates."""


@dataclass(unsafe_hash=True)
class TripleFragmentBase(PydanticModel, ABC):
    """
    Represents part of an RDF triple.
    """

    predicate: Union[str, URIRef]


@dataclass(unsafe_hash=True)
class TripleFragment(TripleFragmentBase):
    """
    Part of an arbitrary RDF triple. Defines the predicate and an object.
    The subject is implicitly defined externally to this class.
    """

    object: Union[str, Identifier]
    subject_hint: RdfSerialisationHint = RdfSerialisationHint.DefaultNode


@dataclass(unsafe_hash=True)
class InverseTripleFragment(TripleFragmentBase):
    """
    Part of an arbitrary RDF triple. Defines the subject and a predicate.
    The object is implicitly defined externally to this class.
    """

    subject: Union[str, Identifier]
    object_hint: RdfSerialisationHint = RdfSerialisationHint.DefaultNode


@dataclass
class ArbitraryRdf(ABC):
    """
    A mixin permitting arbitrary RDF to be added to a qb component.
    """

    @abstractmethod
    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        ...

    @abstractmethod
    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        """
        Defines the set of `RdfSerialisationHint` types which this class can be mapped to.

        `ResourceSerialisationHint.DefaultNode` is permitted by default.
        """
        ...

    @abstractmethod
    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        """Defines the `RdfSerialisationHint` that `RdfSerialisationHint.DefaultNode` maps to."""
        ...

    def get_arbitrary_rdf_fragments(self) -> Set[TripleFragmentBase]:
        return set(self._get_arbitrary_rdf()) 

    def copy_arbitrary_triple_fragments_to_resources(
        self,
        map_target_hint_to_resource: Dict[RdfSerialisationHint, NewResource],
    ):
        """
        Copies the arbitrary RDF defined against this object to `NewResource` s defined in the
        `map_target_hint_to_resource` dict. Takes account of the subject/object hints to place the triple against
        the anticipated RDF resource.
        """
        map_target_hint_to_resource[
            RdfSerialisationHint.DefaultNode
        ] = map_target_hint_to_resource[self.get_default_node_serialisation_hint()]

        permitted_fragment_hints = self.get_permitted_rdf_fragment_hints() | {
            RdfSerialisationHint.DefaultNode
        }
        for fragment in self.get_arbitrary_rdf_fragments():
            if isinstance(fragment, TripleFragment):
                if fragment.subject_hint not in permitted_fragment_hints:
                    raise Exception(
                        f"Fragment hint {fragment.subject_hint} on {self} not permitted."
                    )

                if fragment.subject_hint in map_target_hint_to_resource:
                    resource = map_target_hint_to_resource[fragment.subject_hint]
                    predicate = (
                        fragment.predicate
                        if isinstance(fragment.predicate, URIRef)
                        else URIRef(fragment.predicate)
                    )
                    if isinstance(fragment.object, Identifier):
                        object = fragment.object
                    else:
                        if looks_like_uri(fragment.object):
                            object = Identifier(fragment.object)
                        else:
                            object = Literal(fragment.object)

                    resource.additional_rdf.add((predicate, object))
                else:
                    raise Exception(
                        f"Unhandled fragment hint type {fragment.subject_hint}"
                    )
            elif isinstance(fragment, InverseTripleFragment):
                if fragment.object_hint not in permitted_fragment_hints:
                    raise Exception(
                        f"Fragment hint {fragment.object_hint} on {self} not permitted."
                    )

                if fragment.object_hint in map_target_hint_to_resource:
                    resource = map_target_hint_to_resource[fragment.object_hint]
                    inverse_predicate = InversePredicate(fragment.predicate)
                    subject = (
                        fragment.subject
                        if isinstance(fragment.subject, Identifier)
                        else URIRef(fragment.subject)
                    )
                    resource.additional_rdf.add((inverse_predicate, subject))
                else:
                    raise Exception(
                        f"Unhandled fragment hint type {fragment.object_hint}"
                    )
            else:
                raise Exception(f"Unmatched TripleFragment type {type(fragment)}")
