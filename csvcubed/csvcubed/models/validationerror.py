"""
ValidationError
---------------
"""
from dataclasses import dataclass, field
from abc import ABC, abstractclassmethod

from csvcubedmodels.dataclassbase import DataClassBase


@dataclass
class ValidationError(DataClassBase):
    """Class representing an error validating a model."""

    message: str


@dataclass
class SpecificValidationError(ValidationError, ABC):
    """Abstract base class to represent ValidationErrors which are more specific and so can be interpreted by code."""

    message: str = field(init=False)

    @abstractclassmethod
    def get_error_url(cls) -> str:
        ... 
