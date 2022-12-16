# this class will be class attributes and returns an array of errors

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from csvcubedmodels.dataclassbase import DataClassBase
from csvcubed.models.validationerror import ValidateModelProperiesError
from csvcubed.utils.validations import (
    validate_str_type,
    validate_list_of_str,
    validate_int_type,
)

ValidationFunction = Callable[[Any, str], List[ValidateModelProperiesError]]


class ValidatedModel(DataClassBase):
    def validate(self) -> List[ValidateModelProperiesError]:
        validation_errors: List[ValidateModelProperiesError] = []
        for (property_name, validation_function) in self._get_validations().items():
            print(f"Validating '{property_name}'")
            property_value = getattr(self, property_name)
            validation_errors += validation_function(property_value, property_name)

        return validation_errors

    @abstractmethod
    def _get_validations(self) -> Dict[str, ValidationFunction]:
        pass


@dataclass
class ValidationTester(ValidatedModel):
    string_variable: str

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

    @classmethod
    def _get_validations(cls) -> Dict[str, ValidationFunction]:
        return {"string_variable": validate_str_type}
