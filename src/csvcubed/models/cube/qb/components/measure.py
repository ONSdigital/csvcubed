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
    validate_triple_fragment,
)
from csvcubed.models.cube.qb.components.codelist import NewQbCodeList
from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.models.validatedmodel import ValidatedModel, ValidationFunction
from csvcubed.models.validationerror import ValidateModelProperiesError, ValidationError
from csvcubed.utils.validations import (
    validate_list,
    validate_optional,
    validate_str_type,
    validate_uri,
)
from csvcubed.utils.validators.uri import validate_uri as pydantic_validate_uri

from .datastructuredefinition import SecondaryQbStructuralDefinition

_logger = logging.getLogger(__name__)


@dataclass(unsafe_hash=True)
class QbMeasure(SecondaryQbStructuralDefinition, ValidatedModel, ArbitraryRdf, ABC):
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

    _measure_uri_validator = pydantic_validate_uri("measure_uri")

    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        return []

    def _get_validations(self) -> Dict[str, ValidationFunction]:

        return {
            "measure_uri": validate_uri,
            "arbitrary_rdf": validate_list(validate_triple_fragment),
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

    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        # Leave csv-lint to do the validation here. It will enforce Foreign Key constraints on code lists.
        if isinstance(self.code_list, NewQbCodeList):
            return self.code_list.validate_data(data, column_csv_title)

        return []

    def _get_validations(self) -> Dict[str, ValidationFunction]:

        return {
            "label": validate_str_type,
            "description": validate_optional(validate_str_type),
            "parent_measure_uri": validate_optional(validate_uri),
            "source_uri": validate_optional(validate_uri),
            **UriIdentifiable._get_validations(self),
            "arbitrary_rdf": validate_list(validate_triple_fragment),
        }


def validate_measure(
    value: QbMeasure, property_name: str
) -> List[ValidateModelProperiesError]:
    _logger.debug("Validating a measure %s at property '%s'", value, property_name)
    return value.validate()
