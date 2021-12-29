"""
Concepts
--------

Represent individual concepts inside a `skos:ConceptScheme`.
"""

from dataclasses import dataclass, field
from typing import Optional

from .datastructuredefinition import SecondaryQbStructuralDefinition
from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.utils.uri import uri_safe
from csvcubed.utils.validators.uri import validate_uri


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


@dataclass
class ExistingQbConcept(SecondaryQbStructuralDefinition):
    """Represents a QbConcept which is already defined at the given URI."""

    existing_concept_uri: str

    _existing_concept_uri_validator = validate_uri("existing_concept_uri")


@dataclass
class DuplicatedQbConcept(NewQbConcept, ExistingQbConcept):
    """
    Represents a QbConcept which duplicates an :class:`ExistingQbConcept` with overriding label, notation, etc.

    To be used in a :class:`CompositeQbCodeList`.
    """

    pass
