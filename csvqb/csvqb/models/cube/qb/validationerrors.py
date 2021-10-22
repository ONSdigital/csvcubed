"""
Qb-Cube Validation Errors
-------------------------

:obj:`ValidationError <csvqb.models.validationerror.ValidationError>` models specific to :mod:`qb`.
"""

from dataclasses import dataclass
from typing import Optional, Type, Union

from csvqb.models.cube.qb.components import (
    QbObservationValue,
    QbMultiUnits,
    QbDataStructureDefinition,
)
from csvqb.models.validationerror import SpecificValidationError

ComponentTypeDescription = Union[str, Type[QbDataStructureDefinition]]


def _get_description_for_component(t: ComponentTypeDescription) -> str:
    if isinstance(t, str):
        return t

    return t.__name__


@dataclass
class CsvColumnUriTemplateMissingError(SpecificValidationError):
    """
    Represents an error where the user has defined a component which cannot infer its own csv_column_uri_template without
    manually specifying an csv_column_uri_template.
    """

    csv_column_name: str
    component_type: ComponentTypeDescription

    def __post_init__(self):
        self.message = (
            f"'{self.csv_column_name}' - a {_get_description_for_component(self.component_type)} must have an "
            + "csv_column_uri_template defined."
        )

@dataclass
class CsvColumnLiteralWithUriTemplate(SpecificValidationError):
    """
    Represents an error where the user has defined a literal with a csv_column_uri_template.
    """

    csv_column_name: str
    component_type: ComponentTypeDescription

    def __post_init__(self):
        self.message = (
            f"'{self.csv_column_name}' - a {_get_description_for_component(self.component_type)} cannot have an "
            + "csv_column_uri_template defined."
        )


@dataclass
class MaxNumComponentsExceededError(SpecificValidationError):
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
            f"Found {self.actual_number} of {_get_description_for_component(self.component_type)}s. "
            + f"Expected a maximum of {self.maximum_number}."
        )
        if self.additional_explanation is not None:
            self.message += " " + self.additional_explanation


@dataclass
class MinNumComponentsNotSatisfiedError(SpecificValidationError):
    """
    Represents an error where the user must define a minimum number of components of a given type, but has not done so.
    """

    component_type: ComponentTypeDescription
    minimum_number: int
    actual_number: int
    additional_explanation: Optional[str] = None

    def __post_init__(self):
        self.message = (
            f"At least {self.minimum_number} {_get_description_for_component(self.component_type)}s must be defined."
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
            f"Found {self.actual_number} {_get_description_for_component(self.component_type)}s."
            + f" Expected exactly {self.expected_number}."
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
            f"Found neither {_get_description_for_component(self.component_one)} "
            + f"nor {_get_description_for_component(self.component_two)} defined. "
            + "One of these must be defined."
        )
        if self.additional_explanation is not None:
            self.message += " " + self.additional_explanation


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
            f"Both {_get_description_for_component(self.component_one)} "
            + f"and {_get_description_for_component(self.component_two)} have been defined. "
            + f"These components cannot be used together."
        )
        if self.additional_explanation is not None:
            self.message += " " + self.additional_explanation


@dataclass
class BothUnitTypesDefinedError(IncompatibleComponentsError):
    """
    An error for when the user has both a units column as well as setting `QbObservationValue.unit`.
    """

    component_one: ComponentTypeDescription = f"{QbObservationValue.__name__}.unit"
    component_two: ComponentTypeDescription = QbMultiUnits
    additional_explanation: Optional[str] = None
