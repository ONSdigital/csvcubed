"""
Component Validation Errors
---------------------------

:obj:`ValidationError <csvcubed.models.validationerror.ValidationError>` models specific to :mod:`components`.
"""
import os
from abc import ABC
from dataclasses import dataclass
from typing import ClassVar, Dict, List, Set, Type, Union

from csvcubed.models.validationerror import SpecificValidationError

from .datastructuredefinition import QbStructuralDefinition


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
            f"Found undefined value(s) for '{self.location}' of {self.component}. "
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
class EmptyQbMultiUnitsError(SpecificValidationError):
    """
    An error for when the user has a `QbMultiUnits` but its units
    field is an empty list.
    """

    @classmethod
    def get_error_url(cls) -> str:
        return "http://purl.org/csv-cubed/err/empty-multi-units"

    def __post_init__(self):
        self.message = "The units attribute of a QbMultiUnits must be populated"
