from abc import ABC
from dataclasses import dataclass, field
from typing import Type, Optional, Union

from csvqb.models.cube import (
    QbDataStructureDefinition,
    QbObservationValue,
    QbMultiUnits,
)
from csvqb.models.validationerror import ValidationError


ComponentTypeDescription = Union[str, Type[QbDataStructureDefinition]]


def _get_component_type_description(t: ComponentTypeDescription) -> str:
    if isinstance(t, str):
        return t

    return t.__name__


@dataclass
class SpecificValidationError(ValidationError, ABC):
    """Abstract base class to represent ValidationErrors which are more specific and so can be interpreted by code."""

    message: str = field(init=False)


@dataclass
class OutputUriTemplateMissingError(SpecificValidationError):
    """
    Represents an error where the user has defined a component which cannot infer its own output_uri_template without
    manually specifying an output_uri_template.
    """

    csv_column_name: str
    component_type: ComponentTypeDescription

    def __post_init__(self):
        self.message = (
            f"'{self.csv_column_name}' - an {_get_component_type_description(self.component_type)} must have an "
            + "output_uri_template defined."
        )


@dataclass
class MaximumNumberOfComponentsError(SpecificValidationError):
    """
    Represents an error where the user can define a maximum number of components of a given type, but has defined
    too many.
    """

    component_type: ComponentTypeDescription
    maximum_number: int
    actual_number: int
    additional_explanation: Optional[str] = None

    def __post_init__(self):
        self.message = (
            f"Found {self.actual_number} of {_get_component_type_description(self.component_type)}s. "
            + f"Expected maximum {self.maximum_number}."
        )
        if self.additional_explanation is not None:
            self.message += " " + self.additional_explanation


@dataclass
class MinimumNumberOfComponentsError(SpecificValidationError):
    """
    Represents an error where the user must define a minimum number of components of a given type, but has not done so.
    """

    component_type: ComponentTypeDescription
    minimum_number: int
    actual_number: int
    additional_explanation: Optional[str] = None

    def __post_init__(self):
        self.message = (
            f"At least {self.minimum_number} {_get_component_type_description(self.component_type)}s must be defined."
            + f" Found {self.actual_number}."
        )
        if self.additional_explanation is not None:
            self.message += " " + self.additional_explanation


@dataclass
class WrongNumberComponentsError(SpecificValidationError):
    """
    Represents an error where the user must include a specific number of components, but has not done so.
    """

    component_type: ComponentTypeDescription
    expected_number: int
    actual_number: int
    additional_explanation: Optional[str] = None

    def __post_init__(self):
        self.message = (
            f"Found {self.actual_number} {_get_component_type_description(self.component_type)}s."
            + f" Expected {self.expected_number}."
        )
        if self.additional_explanation is not None:
            self.message += " " + self.additional_explanation


@dataclass
class NeitherDefinedError(SpecificValidationError):
    """
    An error for when the user must define one of two different kinds of component, but has defined neither.
    """

    component_one: ComponentTypeDescription
    component_two: ComponentTypeDescription
    additional_explanation: Optional[str] = None

    def __post_init__(self):
        self.message = (
            f"Found neither {_get_component_type_description(self.component_one)} "
            + f"nor {_get_component_type_description(self.component_two)} defined. "
            + "One of these must be defined."
        )


@dataclass
class UnitsNotDefinedError(NeitherDefinedError):
    """
    An error for when the user has not defined any units for the dataset.
    """

    component_one: ComponentTypeDescription = f"{QbObservationValue.__name__}.unit"
    component_two: ComponentTypeDescription = QbMultiUnits
    additional_explanation: Optional[str] = None


@dataclass
class IncompatibleComponentsError(SpecificValidationError):
    """
    An error for when the user has defined components which are incompatible with each-other.
    """

    component_one: ComponentTypeDescription
    component_two: ComponentTypeDescription
    additional_explanation: Optional[str] = None

    def __post_init__(self):
        self.message = (
            f"Both {_get_component_type_description(self.component_one)} "
            + f"and {_get_component_type_description(self.component_two)} have been defined. "
            + f"These components cannot be used together."
        )


@dataclass
class BothUnitTypesDefinedError(IncompatibleComponentsError):
    """
    An error for when the user has both a units column as well as setting `QbObservationValue.unit`.
    """

    component_one: ComponentTypeDescription = f"{QbObservationValue.__name__}.unit"
    component_two: ComponentTypeDescription = QbMultiUnits
    additional_explanation: Optional[str] = None
