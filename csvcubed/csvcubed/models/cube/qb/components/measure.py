"""
Measures
--------

Represent measures inside an RDF Data Cube.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set
from abc import ABC

from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.models.cube.qb.components.arbitraryrdf import (
    ArbitraryRdf,
    RdfSerialisationHint,
    TripleFragmentBase,
)
from .datastructuredefinition import SecondaryQbStructuralDefinition
from csvcubed.utils.validators.uri import validate_uri


@dataclass
class QbMeasure(SecondaryQbStructuralDefinition, ArbitraryRdf, ABC):
    pass


@dataclass
class ExistingQbMeasure(QbMeasure):
    measure_uri: str
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        return self.arbitrary_rdf

    def __eq__(self, other):
        return (
            isinstance(other, ExistingQbMeasure)
            and self.measure_uri == other.measure_uri
        )

    def __hash__(self):
        return self.measure_uri.__hash__()

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {RdfSerialisationHint.Component}

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.Component

    _measure_uri_validator = validate_uri("measure_uri")


@dataclass
class NewQbMeasure(QbMeasure, UriIdentifiable):
    label: str
    description: Optional[str] = field(default=None, repr=False)
    parent_measure_uri: Optional[str] = field(default=None, repr=False)
    source_uri: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        return self.arbitrary_rdf

    def _get_identifiable_state(self) -> tuple:
        return (
            self.label,
            self.description,
            self.parent_measure_uri,
            self.uri_safe_identifier,
        )

    def __eq__(self, other):
        return (
            isinstance(other, NewQbMeasure)
            and self._get_identifiable_state() == other._get_identifiable_state()
        )

    def __hash__(self):
        return self._get_identifiable_state().__hash__()

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {RdfSerialisationHint.Component, RdfSerialisationHint.Property}

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.Property

    def get_identifier(self) -> str:
        return self.label
