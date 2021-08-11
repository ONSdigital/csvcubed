"""
ValidationError
---------------
"""
from dataclasses import dataclass, field
from abc import ABC


@dataclass
class ValidationError:
    """Class representing an error validating a model."""

    message: str


@dataclass
class SpecificValidationError(ValidationError, ABC):
    """Abstract base class to represent ValidationErrors which are more specific and so can be interpreted by code."""

    message: str = field(init=False)

class UnsupportedDataTypeError(SpecificValidationError):
    """Validation class where end user has opted to use a class we will not support."""

    data_type: str

    def __post_init__(self):
        self.message = f"Literate type '{self.data_type}' not supported"