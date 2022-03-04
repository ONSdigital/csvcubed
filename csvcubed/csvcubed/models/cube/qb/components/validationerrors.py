"""
Component Validation Errors
---------------------------

:obj:`ValidationError <csvcubed.models.validationerror.ValidationError>` models specific to :mod:`components`.
"""
import os
from abc import ABC
from dataclasses import dataclass, field
from typing import Set, List, Dict, Type, ClassVar, Optional, Union

from .datastructuredefinition import QbStructuralDefinition
from csvcubed.models.validationerror import (
    SpecificValidationError,
    PydanticValidationError,
    PydanticThrowableSpecificValidationError,
)


@dataclass
class UndefinedValuesError(SpecificValidationError, ABC):
    """
    An error which occurs when we find an value which is not defined in our list of appropriate values

    (e.g. a dimension column contains values not in the defined code list)
    """

    component: QbStructuralDefinition
    """The component where the undefined values were found."""

    undefined_values: Set[str]

    location: str
    """The property or location where the undefined values were found."""

    def __post_init__(self):
        unique_values_to_display: str = (
            f"{list(self.undefined_values)[:4]}..."
            if len(self.undefined_values) > 5
            else str(self.undefined_values)
        )
        self.message = (
            f'Found undefined value(s) for "{self.location}" of {self.component}. '
            + f"Undefined values: {unique_values_to_display}"
        )


@dataclass
class UndefinedMeasureUrisError(UndefinedValuesError):
    """
    An error which occurs when URIs for measures in a multi-measure dimension column are not defined in the list of
    new measure definitions.
    """

    location: str = "measure URI"

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/undef-meas"


@dataclass
class UndefinedUnitUrisError(UndefinedValuesError):
    """
    An error which occurs when URIs for units in a units column are not defined in the list of
    new unit definitions.
    """

    location: str = "unit URI"

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/undef-unit"


@dataclass
class UndefinedAttributeValueUrisError(UndefinedValuesError):
    """
    An error which occurs when URIs for attribute values in an attribute column are not defined in the list of
    new attribute value definitions.
    """

    location: str = "attribute value URI"

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/undef-attrib"


@dataclass
class LabelUriCollisionError(SpecificValidationError):
    """
    An error which occurs when the user has defined multiple resources which have different labels which would
    utilise the same URI.
    """

    csv_column_name: str
    conflicting_values: List[str]
    conflicting_identifier: str

    @classmethod
    def get_error_url(cls) -> str:
        raise Exception("Exception should never be presented to user.")

    def __post_init__(self):
        label_values = ", ".join([f'"{v}"' for v in self.conflicting_values])
        self.message = (
            f'Labels "{label_values}" collide as single uri-safe value "{self.conflicting_identifier}" '
            f'in column "{self.csv_column_name}"'
        )


@dataclass
class ReservedUriValueError(PydanticThrowableSpecificValidationError):
    """
    An error which occurs when the user has defined a resource which would re-use a reserved URI value.
    """

    component: Type[QbStructuralDefinition]
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
class ConflictingUriSafeValuesError(PydanticThrowableSpecificValidationError):
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
            [f"'{label}'" for label in conflicting_labels]
        )

    def __post_init__(self):
        conflicting_values_lines = [
            self._generate_conflicting_values_string(uri_val, conflicting_labels)
            for uri_val, conflicting_labels in self.map_uri_safe_values_to_conflicting_labels.items()
        ]

        self.message = (
            f"Conflicting URIs: {self._indented_line_sep}"
            + self._indented_line_sep.join(conflicting_values_lines)
        )

    @classmethod
    def get_error_url(cls) -> str:
        return "https://purl.org/csv-cubed/err/conflict-uri"
