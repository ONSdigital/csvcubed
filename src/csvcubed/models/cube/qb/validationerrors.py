"""
Qb-Cube Validation Errors
-------------------------

:obj:`ValidationError <csvcubed.models.validationerror.ValidationError>` models specific to :mod:`qb`.
"""

import os
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Optional, Type, Union

from csvcubed.models.validationerror import SpecificValidationError

from ..qb import (
    QbDimension,
    QbMultiMeasureDimension,
    QbMultiUnits,
    QbObservationValue,
    QbStructuralDefinition,
)

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
        return "http://purl.org/csv-cubed/err/csv-col-uri-temp-mis"

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
        return "http://purl.org/csv-cubed/err/csv-col-lit-uri-temp"

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
        return "http://purl.org/csv-cubed/err/multi-meas-col"


@dataclass
class MoreThanOneUnitsColumnError(MaxNumComponentsExceededError):
    """
    More than one multi-units column has been defined in a cube.
    """

    maximum_number: int = 1
    component_type: ComponentTypeDescription = QbMultiUnits

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/multi-unit-col"


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
        return "http://purl.org/csv-cubed/err/no-dim"


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
        return "http://purl.org/csv-cubed/err/no-unit"


@dataclass
class NoMeasuresDefinedError(NeitherDefinedError):
    """
    An error for when the user has not defined any measures for the dataset.
    """

    component_one: ComponentTypeDescription = f"{QbObservationValue.__name__}.measure"
    component_two: ComponentTypeDescription = QbMultiMeasureDimension

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/no-meas"


@dataclass
class NoObservedValuesColumnDefinedError(MinNumComponentsNotSatisfiedError):
    """
    An error for when the user has not defined any observed value columns for the dataset.
    """

    component_type: ComponentTypeDescription = QbObservationValue
    minimum_number: int = 1
    actual_number: int = 0

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/no-obsv-col"


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
        return "http://purl.org/csv-cubed/err/both-unit-typ-def"


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
        return "http://purl.org/csv-cubed/err/both-meas-typ-def"


@dataclass
class EmptyQbMultiMeasureDimensionError(SpecificValidationError):
    """
    An error for when the user has a `QbMultiMeasureDimension` but its measure
    field is an empty list.
    """

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/empty-multi-meas-dimension"

    def __post_init__(self):
        self.message = (
            "The field attribute of a QbMultiMeasureDimension must be populated"
        )


@dataclass
class PivotedShapeMeasureColumnsExistError(BothMeasureTypesDefinedError):
    """
    An error to inform the user that they have attempted to define a pivoted shape cube with measure columns.
    """

    measure_col_titles: List[str] = field(default_factory=list)
    column_names_concatenated: str = field(init=False)

    additional_explanation: Optional[str] = None

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/piv-shape-meas-cols-exist"

    def __post_init__(self):
        self.column_names_concatenated = ", ".join(self.measure_col_titles)
        self.message = f"The cube is in pivoted shape, but 1 or more measure columns have been defined. These two approaches are incompatible."


@dataclass
class DuplicateMeasureError(SpecificValidationError):
    """
    An error to inform the user that they have defined a pivoted cube in which multiple
    observation value columns are described using the same measure.
    """

    column_names: List[str]
    column_names_concatenated: str = field(init=False)

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/dup-measure"

    def __post_init__(self):
        self.column_names_concatenated = ", ".join(sorted(self.column_names))
        self.message = f"In the pivoted shape, two or more observation value columns cannot be represented by identical measures. {self.column_names_concatenated}"


@dataclass
class AttributeNotLinkedError(SpecificValidationError):
    """
    An error to inform the user that the units or attribute column is defined but it is not linked to the obs column
    """

    attribute_column_title: str

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/att-not-linked"

    def __post_init__(self):
        self.message = f"Units or attribute column '{self.attribute_column_title}' is defined but it is not linked to an observed values column"


@dataclass
class LinkedObsColumnDoesntExistError(SpecificValidationError):
    """
    An error to infrom the user that the units or attribute column is defined for which obs val column doesn't appear to exist.
    """

    alleged_obs_val_column_title: str
    attribute_column_title: str

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/link-obs-col-not-exist"

    def __post_init__(self):
        self.message = f"The unit or attribute column '{self.attribute_column_title}' is defined for an observed value column '{self.alleged_obs_val_column_title}' that doesn't appear to exist."


@dataclass
class LinkedToNonObsColumnError(SpecificValidationError):
    """
    An error to infrom the user that units or attribute column is defined in which
    the linked obs val column isn't actually an observations column.
    """

    alleged_obs_val_column_title: str
    attribute_column_title: str

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/link-non-obs-col"

    def __post_init__(self):
        self.message = f"Units or attribute column '{self.attribute_column_title}' is defined but the linked observation column '{self.alleged_obs_val_column_title}' is not actually an observation column"


@dataclass
class HybridShapeError(SpecificValidationError):
    """
    An Error where there are mutliple obs val columns defined without measures, and at least one measure column defined.
    This is an erroneous hybrid between standard and pivoted shape.
    """

    not_linked_obs_val_cols: List[str]
    measure_cols: List[str]

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/hybrid-shape"

    def __post_init__(self):

        not_linked_cols = ", ".join(str(self.not_linked_obs_val_cols))
        measure_cols = ", ".join(str(self.measure_cols))
        self.message = (
            f"Found these observation value columns without measures linked: '{not_linked_cols}'."
            + os.linesep
            + f"But found these measure columns '{measure_cols}. "
            + os.linesep
            + "This does not conform with either the standard or pivoted shape of expected data."
        )


@dataclass
class PivotedObsValColWithoutMeasureError(SpecificValidationError):
    """
    An error to inform the user that they have defined a pivoted cube in which an
    observation value column has been defined without a measure linked either within
    the column or from a measure column.
    """

    no_measure_obs_col_titles: List[str] = field(default_factory=list)
    column_names_concatenated: str = field(init=False)
    additional_explanation: Optional[str] = None

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/piv-obsv-col-no-measure"

    def __post_init__(self):
        no_measure_obs_cols = ", ".join(str(self.no_measure_obs_col_titles))
        self.message = f"Cube is in the pivoted shape but observation value column(s): '{no_measure_obs_cols}' have been defined without a measure linked within the column definition."
