"""this class will be class attributes and returns an array of errors"""

import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, TypeVar, Union

from csvcubedmodels.dataclassbase import DataClassBase

from csvcubed.models.validationerror import ValidateModelPropertiesError

ValidationFunction = Callable[[Any, List[str]], List[ValidateModelPropertiesError]]

T = TypeVar("T", bound="ValidatedModel")


@dataclass
class Validations(Generic[T]):
    """
    This class holds the validations which should be executed against a given model.
    """

    individual_property_validations: Dict[str, ValidationFunction]
    whole_object_validations: List[
        Callable[[T, List[str]], List[ValidateModelPropertiesError]]
    ] = field(default_factory=list)


@dataclass
class ValidatedModel(DataClassBase):
    """This abstract class that will act as a parent class for class attribute validations.
    The class will run a valdiation function for each attribute that is passed in and return either a list of errors or an empty list.
    """

    def validate(
        self, property_path: List[str] = []
    ) -> List[ValidateModelPropertiesError]:
        """
        The validate function will go through each attribute and the corresponding validation function and
         collect the validation errors(if there is any) and return the variable names and the error messages.
        """
        validation_errors: List[ValidateModelPropertiesError] = []
        validations = self._get_validations()
        if isinstance(validations, Validations):
            validation_errors += self._apply_individual_property_validations(
                validations.individual_property_validations, property_path
            )

            for whole_obj_validator in validations.whole_object_validations:
                validation_errors += whole_obj_validator(self, property_path)
        else:
            validation_errors += self._apply_individual_property_validations(
                validations, property_path
            )

        return validation_errors

    def _apply_individual_property_validations(
        self,
        individual_property_validations: Dict[str, ValidationFunction],
        property_path: List[str],
    ) -> List[ValidateModelPropertiesError]:
        validation_errors: List[ValidateModelPropertiesError] = []

        for (
            property_name,
            validation_function,
        ) in individual_property_validations.items():
            new_property_path = [*property_path, property_name]
            logging.debug("Validating %s", property_name)

            property_value = getattr(self, property_name)
            errs = validation_function(property_value, new_property_path)

            if any(errs):
                logging.debug("'%s' generated errors: %s", property_name, errs)

            validation_errors += errs

        return validation_errors

    @abstractmethod
    def _get_validations(self) -> Union[Validations, Dict[str, ValidationFunction]]:
        pass
