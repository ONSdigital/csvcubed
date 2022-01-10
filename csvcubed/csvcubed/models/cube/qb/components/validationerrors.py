"""
Component Validation Errors
---------------------------

:obj:`ValidationError <csvcubed.models.validationerror.ValidationError>` models specific to :mod:`components`.
"""
from abc import ABC
from dataclasses import dataclass
from typing import Set

from .datastructuredefinition import QbStructuralDefinition
from csvcubed.models.validationerror import SpecificValidationError


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


@dataclass
class UndefinedUnitUrisError(UndefinedValuesError):
    """
    An error which occurs when URIs for units in a units column are not defined in the list of
    new unit definitions.
    """

    location: str = "unit URI"


@dataclass
class UndefinedAttributeValueUrisError(UndefinedValuesError):
    """
    An error which occurs when URIs for attribute values in an attribute column are not defined in the list of
    new attribute value definitions.
    """

    location: str = "attribute value URI"
