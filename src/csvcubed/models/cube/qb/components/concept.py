"""
Concepts
--------

Represent individual concepts inside a `skos:ConceptScheme`.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.models.validatedmodel import ValidatedModel, ValidationFunction
from csvcubed.utils import validations as v
from csvcubed.utils.uri import uri_safe

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

    def _get_validations(self) -> Dict[str, ValidationFunction]:

        return {
            "label": v.string,
            "code": v.string,
            "parent_code": v.optional(v.string),
            "sort_order": v.optional(v.integer),
            "description": v.optional(v.string),
            **UriIdentifiable._get_validations(self),
        }


@dataclass
class ExistingQbConcept(SecondaryQbStructuralDefinition):
    """Represents a QbConcept which is already defined at the given URI."""

    existing_concept_uri: str

    def _get_validations(self) -> Dict[str, ValidationFunction]:

        return {
            "existing_concept_uri": v.uri,
        }


@dataclass(unsafe_hash=True)
class DuplicatedQbConcept(NewQbConcept, ExistingQbConcept):
    """
    Represents a QbConcept which duplicates an :class:`ExistingQbConcept` with overriding label, notation, etc.

    To be used in a :class:`CompositeQbCodeList`.
    """

    def _get_validations(self) -> Dict[str, ValidationFunction]:

        return {
            **ExistingQbConcept._get_validations(self),
            **NewQbConcept._get_validations(self),
        }
