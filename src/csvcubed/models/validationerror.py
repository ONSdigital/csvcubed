"""
ValidationError
---------------
"""
import os
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Optional, Set, Type, Union

from csvcubedmodels.dataclassbase import DataClassBase

from csvcubed.models.errorurl import HasErrorUrl


@dataclass
class ValidationError(DataClassBase):
    """Class representing an error validating a model."""

    message: str


@dataclass
class SpecificValidationError(ValidationError, HasErrorUrl, ABC):
    """Abstract base class to represent ValidationErrors which are more specific and so can be interpreted by code."""

    message: str = field(init=False)


@dataclass
class ValidateModelPropertiesError(ValidationError):

    """
    This error will be returned with the path of the offending value that has not been validated.
    """

    property_path: List[str]
    offending_value: Any

    def __post_init__(self):
        self.message += f" Check the following variable at the property path: '{self.property_path}'"


@dataclass
class ReservedUriValueError(ValidateModelPropertiesError, HasErrorUrl):
    """
    An error which occurs when the user has defined a resource which would re-use a reserved URI value.
    """

    component: Type
    """The type of component where the conflicting values were found."""
    conflicting_values: List[str]
    reserved_identifier: str

    @classmethod
    def get_error_url(cls) -> str:
        return "https://purl.org/csv-cubed/err/resrv-uri-val"

    def __post_init__(self):
        label_values = ", ".join([f'"{v}"' for v in self.conflicting_values])
        self.message = (
            f'Label(s) {label_values} used in "{self.component.__name__}" component. '
            + f'"{self.reserved_identifier}" is a reserved identifier and cannot be used in code-lists.'
        )


@dataclass
class ConflictingUriSafeValuesError(ValidateModelPropertiesError, HasErrorUrl):
    """
    An error which happens when the user has multiple resources which would generate the same URI-safe value.
    This conflict must be resolved by the user before it is possible to continue.
    """

    component_type: Union[Type, str]
    """The component type where the conflicting values were found."""

    map_uri_safe_values_to_conflicting_labels: Dict[str, Set[str]]

    _indented_line_sep: ClassVar[str] = f"{os.linesep}    "

    @staticmethod
    def _generate_conflicting_values_string(
        uri_val: str, conflicting_labels: Set[str]
    ) -> str:
        return f"{uri_val}: " + ", ".join(
            [f"'{label}'" for label in sorted(conflicting_labels)]
        )

    def __post_init__(self):
        conflicting_values_lines = [
            self._generate_conflicting_values_string(uri_val, conflicting_labels)
            for uri_val, conflicting_labels in self.map_uri_safe_values_to_conflicting_labels.items()
        ]

        self.message = (
            f"Conflicting URIs: {self._indented_line_sep}"
            + self._indented_line_sep.join(sorted(conflicting_values_lines))
        )

    @classmethod
    def get_error_url(cls) -> str:
        return "https://purl.org/csv-cubed/err/conflict-uri"
