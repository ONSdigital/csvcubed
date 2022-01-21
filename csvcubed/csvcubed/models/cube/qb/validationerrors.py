"""
Qb-Cube Validation Errors
-------------------------

:obj:`ValidationError <csvcubed.models.validationerror.ValidationError>` models specific to :mod:`qb`.
"""

from dataclasses import dataclass
from typing import Optional, Type, Union
from abc import ABC

from ..qb import (
    QbMultiMeasureDimension,
    QbDimension,
    QbSingleMeasureObservationValue,
    QbMultiMeasureObservationValue,
    QbObservationValue,
    QbMultiUnits,
    QbStructuralDefinition,
)
from csvcubed.models.validationerror import SpecificValidationError

ComponentTypeDescription = Union[str, Type[QbStructuralDefinition]]


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

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/csv-col-uri-temp-mis'

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

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/csv-col-lit-uri-temp'

    def __post_init__(self):
        self.message = (
            f"'{self.csv_column_name}' - a {_get_description_for_component(self.component_type)} cannot have a "
            + "csv_column_uri_template defined."
        )


@dataclass
class MaxNumComponentsExceededError(SpecificValidationError, ABC):
    """
    Represents an error where the user can define a maximum number of components of a given type, but has defined
    too many.
    """

    actual_number: int
    component_type: ComponentTypeDescription
    maximum_number: int
    additional_explanation: Optional[str] = None

    def __post_init__(self):
        self.message = (
            f"Found {self.actual_number} of {_get_description_for_component(self.component_type)}s. "
            + f"Expected a maximum of {self.maximum_number}."
        )
        if self.additional_explanation is not None:
            self.message += " " + self.additional_explanation


@dataclass
class MoreThanOneDefinedError(MaxNumComponentsExceededError, ABC):
    """
    More than one instance of a component has been found. A maximum of one of these components can be defined per cube.
    """

    maximum_number: int = 1


@dataclass
class MoreThanOneMeasureColumnError(MaxNumComponentsExceededError):
    """
    More than one multi-measure columns has been defined in a cube.
    """

    maximum_number: int = 1
    component_type: ComponentTypeDescription = QbMultiMeasureDimension

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/multi-meas-col'


@dataclass
class MoreThanOneUnitsColumnError(MaxNumComponentsExceededError):
    """
    More than one multi-units column has been defined in a cube.
    """

    maximum_number: int = 1
    component_type: ComponentTypeDescription = QbMultiUnits

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/multi-unit-col'


@dataclass
class MoreThanOneObservationsColumnError(MaxNumComponentsExceededError):
    """
    An error where more than one observations column has been defined in a cube.
    """

    maximum_number: int = 1
    component_type: ComponentTypeDescription = QbObservationValue

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/multi-obsv-col'


@dataclass
class MinNumComponentsNotSatisfiedError(SpecificValidationError, ABC):
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
class NoDimensionsDefinedError(MinNumComponentsNotSatisfiedError):
    """
    Represents an error where no dimensions have been defined in a cube.
    """

    component_type: ComponentTypeDescription = QbDimension
    minimum_number: int = 1
    actual_number: int = 0

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/no-dim'


@dataclass
class WrongNumberComponentsError(SpecificValidationError, ABC):
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
class NeitherDefinedError(SpecificValidationError, ABC):
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
class NoUnitsDefinedError(NeitherDefinedError):
    """
    An error for when the user has not defined any units for the dataset.
    """

    component_one: ComponentTypeDescription = f"{QbObservationValue.__name__}.unit"
    component_two: ComponentTypeDescription = QbMultiUnits

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/no-unit'


@dataclass
class NoMeasuresDefinedError(NeitherDefinedError):
    """
    An error for when the user has not defined any measures for the dataset.
    """

    component_one: ComponentTypeDescription = f"{QbObservationValue.__name__}.measure"
    component_two: ComponentTypeDescription = QbMultiMeasureDimension

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/no-meas'


@dataclass
class NoObservedValuesColumnDefinedError(NeitherDefinedError):
    """
    An error for when the user has not defined any observed value columns for the dataset.
    """

    component_one: ComponentTypeDescription = QbSingleMeasureObservationValue
    component_two: ComponentTypeDescription = QbMultiMeasureObservationValue

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/no-obsv-col'


@dataclass
class IncompatibleComponentsError(SpecificValidationError, ABC):
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

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/both-unit-typ-def'


@dataclass
class BothMeasureTypesDefinedError(IncompatibleComponentsError):
    """
    An error for when the user has both a measure dimension column as well as setting `QbObservationValue.measure`.
    """

    component_one: ComponentTypeDescription = f"{QbObservationValue.__name__}.measure"
    component_two: ComponentTypeDescription = QbMultiMeasureDimension
    additional_explanation: Optional[str] = None

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/both-meas-typ-def'
