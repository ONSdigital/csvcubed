"""
Measures
--------

Represent measures inside an RDF Data Cube.
"""
import logging
from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import pandas as pd

from csvcubed.models.cube.qb.components.arbitraryrdf import (
    ArbitraryRdf,
    RdfSerialisationHint,
    TripleFragmentBase,
)
from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.models.validatedmodel import ValidationFunction
from csvcubed.utils import validations as v

from .datastructuredefinition import SecondaryQbStructuralDefinition

_logger = logging.getLogger(__name__)


@dataclass(unsafe_hash=True)
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

    def _get_validations(self) -> Dict[str, ValidationFunction]:

        return {
            "measure_uri": v.uri,
            "arbitrary_rdf": v.list(v.validated_model(TripleFragmentBase)),
        }


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

    def _get_validations(self) -> Dict[str, ValidationFunction]:

        return {
            "label": v.string,
            "description": v.optional(v.string),
            "parent_measure_uri": v.optional(v.uri),
            "source_uri": v.optional(v.uri),
            **UriIdentifiable._get_validations(self),
            "arbitrary_rdf": v.list(v.validated_model(TripleFragmentBase)),
        }
