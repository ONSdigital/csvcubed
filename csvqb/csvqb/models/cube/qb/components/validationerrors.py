"""
Component Validation Errors
-----------------

:obj:`ValidationError <csvqb.models.validationerror.ValidationError>` models specific to :mod:`components`.
"""

from dataclasses import dataclass
from typing import Set

from .datastructuredefinition import QbDataStructureDefinition
from csvqb.models.validationerror import SpecificValidationError


@dataclass
class UndefinedValuesError(SpecificValidationError):
    """
    An error which occurs when we find an value which is not defined in our list of appropriate values

    (e.g. a dimension column contains values not in the defined code list)
    """

    component: QbDataStructureDefinition
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
