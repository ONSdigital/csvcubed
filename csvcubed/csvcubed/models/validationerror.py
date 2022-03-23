"""
ValidationError
---------------
"""
from dataclasses import dataclass, field
from abc import ABC
from typing import List, Optional

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
class PydanticValidationError(ValidationError, ABC):
    """
    The error type returned from pydantic validation functionality.
    """

    path: List[str] = field(init=False, default_factory=lambda: [])
    """
    Place to for pydantic validation to set the object path where this error occurred.
    """


@dataclass
class UnknownPydanticValidationError(PydanticValidationError):
    """
    The error type for a generic type of error raised by pydantic which we don't handle by default.
    """

    path: List[str] = field(init=True)
    original_error: Optional[Exception] = field(default=None)

    def __post_init__(self):
        self.message = f"{', '.join(self.path)} - {self.original_error}"


@dataclass
class PydanticThrowableSpecificValidationError(
    SpecificValidationError, PydanticValidationError, ValueError, ABC
):
    """
    This error extends :class:`ValueError` in order for it to be possible for it to be raised as an exception
    in a pydantic validation function.
    """

    pass
