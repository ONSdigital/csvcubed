"""
Concepts
--------

Represent individual concepts inside a `skos:ConceptScheme`.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd

from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.models.validatedmodel import ValidatedModel, ValidationFunction
from csvcubed.models.validationerror import ValidationError
from csvcubed.utils.uri import uri_safe
from csvcubed.utils.validations import (
    validate_optional,
    validate_str_type,
    validate_uri,
)
from csvcubed.utils.validators.uri import validate_uri as pydantic_validate_uri

from .datastructuredefinition import SecondaryQbStructuralDefinition


@dataclass(eq=False, unsafe_hash=False)
class NewQbConcept(SecondaryQbStructuralDefinition, UriIdentifiable):

    label: str
    code: str = field(default="")
    parent_code: Optional[str] = field(default=None, repr=False)
    sort_order: Optional[int] = field(default=None, repr=False)
    description: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)

    def get_identifier(self) -> str:
        return self.code

    def __post_init__(self):
        if self.code.strip() == "":
            self.code = uri_safe(self.label)

    def __eq__(self, other):
        return isinstance(other, NewQbConcept) and self.code == other.code

    def __hash__(self):
        return self.code.__hash__()

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
            "label": validate_str_type,
            "code": validate_str_type,
            "parent_code": validate_optional(validate_str_type),
            "sort_order": validate_optional(validate_str_type),
            "description": validate_optional(validate_str_type),
            **UriIdentifiable._get_validations(self),
        }


@dataclass
class ExistingQbConcept(SecondaryQbStructuralDefinition):
    """Represents a QbConcept which is already defined at the given URI."""

    existing_concept_uri: str

    _existing_concept_uri_validator = pydantic_validate_uri("existing_concept_uri")

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
            "existing_concept_uri": validate_uri,
        }


@dataclass(unsafe_hash=True)
class DuplicatedQbConcept(NewQbConcept, ExistingQbConcept, ValidatedModel):
    """
    Represents a QbConcept which duplicates an :class:`ExistingQbConcept` with overriding label, notation, etc.

    To be used in a :class:`CompositeQbCodeList`.
    """

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
            **ExistingQbConcept._get_validations(self),
            **NewQbConcept._get_validations(self),
        }
