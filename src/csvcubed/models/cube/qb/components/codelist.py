"""
Code Lists
----------

Represent code lists in an RDF Data Cube.
"""
from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Generic, List, Optional, Set, TypeVar

from csvcubed.inputs import PandasDataTypes, pandas_input_to_columnar_str
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.validatedmodel import ValidationFunction
from csvcubed.models.validationerror import (
    ReservedUriValueError,
    ValidateModelPropertiesError,
    ValidationError,
)
from csvcubed.utils import validations as v
from csvcubed.utils.qb.validation.uri_safe import ensure_no_uri_safe_conflicts
from csvcubed.writers.helpers.skoscodelistwriter.constants import SCHEMA_URI_IDENTIFIER

from ...uristyle import URIStyle
from .arbitraryrdf import ArbitraryRdf, RdfSerialisationHint, TripleFragmentBase
from .concept import DuplicatedQbConcept, NewQbConcept
from .datastructuredefinition import SecondaryQbStructuralDefinition


@dataclass
class QbCodeList(SecondaryQbStructuralDefinition, ABC):
    pass


@dataclass
class ExistingQbCodeList(QbCodeList):
    """
    Contains metadata necessary to link a dimension to an existing skos:ConceptScheme.
    """

    concept_scheme_uri: str

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {"concept_scheme_uri": v.uri}


TNewQbConcept = TypeVar("TNewQbConcept", bound=NewQbConcept, covariant=True)


@dataclass
class NewQbCodeList(QbCodeList, ArbitraryRdf, Generic[TNewQbConcept]):
    """
    Contains the metadata necessary to create a new skos:ConceptScheme which is local to a dataset.
    """

    metadata: CatalogMetadata
    concepts: List[TNewQbConcept]
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)
    uri_style: Optional[URIStyle] = None

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {
            "metadata": v.validated_model(CatalogMetadata),
            "concepts": v.all_of(
                v.list(v.validated_model(NewQbConcept)),
                self._ensure_no_use_of_reserved_keywords,
                self._validate_concepts_non_conflicting,
            ),
            "arbitrary_rdf": v.list(v.validated_model(TripleFragmentBase)),
            "uri_style": v.optional(v.enum(URIStyle)),
        }

    @staticmethod
    def _ensure_no_use_of_reserved_keywords(
        concepts: List[TNewQbConcept], property_path: List[str]
    ) -> List[ValidateModelPropertiesError]:
        conflicting_values: List[str] = []
        for concept in concepts:
            if concept.uri_safe_identifier == SCHEMA_URI_IDENTIFIER:
                conflicting_values.append(concept.label)

        if any(conflicting_values):
            return [
                ReservedUriValueError(
                    message="",  # Message gets defined in __post_init__.
                    component=NewQbCodeList,
                    property_path=property_path,
                    offending_value=concepts,
                    conflicting_values=conflicting_values,
                    reserved_identifier=SCHEMA_URI_IDENTIFIER,
                )
            ]

        return []

    @staticmethod
    def _validate_concepts_non_conflicting(
        concepts: List[TNewQbConcept], property_path: List[str]
    ) -> List[ValidateModelPropertiesError]:
        """
        Ensure that there are no collisions where multiple concepts map to the same URI-safe value.
        """
        return ensure_no_uri_safe_conflicts(
            [(concept.label, concept.uri_safe_identifier) for concept in concepts],
            NewQbCodeList,
            property_path,
            concepts,
        )

    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        return self.arbitrary_rdf

    @staticmethod
    def from_data(
        metadata: CatalogMetadata,
        data: PandasDataTypes,
        uri_style: Optional[URIStyle] = None,
    ) -> "NewQbCodeList":
        columnar_data = pandas_input_to_columnar_str(data)
        concepts = [NewQbConcept(c) for c in sorted(set(columnar_data))]
        return NewQbCodeList(metadata, concepts, uri_style=uri_style)

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {
            RdfSerialisationHint.CatalogDataset,
            RdfSerialisationHint.ConceptScheme,
        }

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.ConceptScheme

    def validate_data(
        self, data: PandasDataTypes, column_csv_title: str
    ) -> list[ValidationError]:
        """
        Validate the data held in the codelists, assuming case insensitivity
        """
        return []


@dataclass
class CompositeQbCodeList(NewQbCodeList[DuplicatedQbConcept]):
    """Represents a :class:`NewQbCodeList` made from a set of :class:`DuplicatedQbConcept` instances."""

    variant_of_uris: List[str] = field(default_factory=list)

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {
            **NewQbCodeList._get_validations(self),
            "variant_of_uris": v.list(v.uri),
        }
