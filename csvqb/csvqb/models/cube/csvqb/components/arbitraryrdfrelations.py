"""
Arbitrary RDF Container
-----------------------

Defines a mixin permitting arbitrary RDF to be added to a qb component.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Set, Dict, Union
from rdflib.term import Identifier, URIRef
from sharedmodels.rdf import NewResource, InversePredicate

from csvqb.models.pydanticmodel import PydanticModel


class ResourceSerialisationHint(Enum):
    """
    Provides a hint as to which RDF resource to serialise the triple fragment against.
    """

    DefaultNode = (0,)
    """The primary RDF node that the class generates."""

    Component = 1
    """The `qb:Component` that the class generates (if any)."""

    Property = 2
    """The `rdf:Property` that the class generates (if any)"""


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
    subject_hint: ResourceSerialisationHint = ResourceSerialisationHint.DefaultNode


@dataclass(unsafe_hash=True)
class InverseTripleFragment(TripleFragmentBase):
    """
    Part of an arbitrary RDF triple. Defines the subject and a predicate.
    The object is implicitly defined externally to this class.
    """

    subject: Union[str, Identifier]
    object_hint: ResourceSerialisationHint = ResourceSerialisationHint.DefaultNode


class ArbitraryRdfRelations(ABC):
    """
    A mixin permitting arbitrary RDF to be added to a qb component.
    """

    @abstractmethod
    def arbitrary_rdf(self) -> Set[TripleFragmentBase]:
        """Defines the arbitrary RDF related to this entity which should be serialised."""
        ...

    @abstractmethod
    def get_permitted_rdf_fragment_hints(self) -> Set[ResourceSerialisationHint]:
        """Defines the set of `RdfFragmentHint` types which this class can be mapped to."""
        ...

    def get_arbitrary_rdf_fragments(self) -> Set[TripleFragmentBase]:
        return self.arbitrary_rdf  # type: ignore

    def copy_arbitrary_triple_fragments_to_resources(
        self,
        map_target_hint_to_resource: Dict[ResourceSerialisationHint, NewResource],
    ):
        """
        Copies the arbitrary RDF defined against this object to `NewResource` s defined in the
        `map_target_hint_to_resource` dict. Takes account of the subject/object hints to place the triple against
        the anticipated RDF resource.
        """

        permitted_fragment_hints = self.get_permitted_rdf_fragment_hints()
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
                    object = (
                        fragment.object
                        if isinstance(fragment.object, Identifier)
                        else Identifier(fragment.object)
                    )
                    resource.additional_rdf[predicate] = object
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
                    resource.additional_rdf[inverse_predicate] = subject
                else:
                    raise Exception(
                        f"Unhandled fragment hint type {fragment.object_hint}"
                    )
            else:
                raise Exception(f"Unmatched TripleFragment type {type(fragment)}")
