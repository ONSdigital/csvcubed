"""
Component Validation Errors
---------------------------

:obj:`ValidationError <csvcubed.models.validationerror.ValidationError>` models specific to :mod:`components`.
"""

from dataclasses import dataclass
from typing import Set, List

from .datastructuredefinition import QbStructuralDefinition
from csvcubed.models.validationerror import SpecificValidationError


@dataclass
class UndefinedValuesError(SpecificValidationError):
    """
    An error which occurs when we find an value which is not defined in our list of appropriate values

    (e.g. a dimension column contains values not in the defined code list)
    """

    component: QbStructuralDefinition
    """The component where the undefined values were found."""

    location: str
    """The property or location where the undefined values were found."""

    undefined_values: Set[str]

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
class LabelUriCollisionError(SpecificValidationError):
    """
    An error which occurs when the user has defined multiple resources which have different labels which would
    utilise the same URI.
    """

    csv_column_name: str
    conflicting_values: List[str]
    conflicting_identifier: str

    def __post_init__(self):
        label_values = ", ".join([f'"{v}"' for v in self.conflicting_values])
        self.message = (
            f'Labels "{label_values}" collide as single uri-safe value "{self.conflicting_identifier}" '
            f'in column "{self.csv_column_name}"'
        )


@dataclass
class ReservedUriValueError(SpecificValidationError):
    """
    An error which occurs when the user has defined a resource which would re-use a reserved URI value.
    """

    csv_column_name: str
    conflicting_values: List[str]
    reserved_identifier: str

    def __post_init__(self):
        label_values = ", ".join([f'"{v}"' for v in self.conflicting_values])
        self.message = (
            f'Label(s) {label_values} used in column "{self.csv_column_name}". '
            + f'"{self.reserved_identifier}" is a reserved identifier and cannot be used in code-lists.'
        )
