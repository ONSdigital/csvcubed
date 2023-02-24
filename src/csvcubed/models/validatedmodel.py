"""this class will be class attributes and returns an array of errors"""

import logging
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from csvcubedmodels.dataclassbase import DataClassBase

from csvcubed.models.validationerror import ValidateModelProperiesError

ValidationFunction = Callable[[Any, str], List[ValidateModelProperiesError]]


class ValidatedModel(DataClassBase):
    """This abrstract class that will act as a parent class for class attribute validations.
    The class will run a valdiation function for each attribute that is passed in and return either a list of errors or an emtpry list.
    """

    def validate(self) -> List[ValidateModelProperiesError]:
        """
        The validate function will go through each attribute and the corresponding validation function and
         collect the validation errors(if there is any) and return the variable names and the error messages.
        """
        validation_errors: List[ValidateModelProperiesError] = []
        for (property_name, validation_function) in self._get_validations().items():
            logging.debug("Validating %s", property_name)

            property_value = getattr(self, property_name)
            errs = validation_function(property_value, property_name)

            if any(errs):
                logging.debug("'%s' generated errors: %s", property_name, errs)

            validation_errors += errs

        return validation_errors

    @abstractmethod
    def _get_validations(self) -> Dict[str, ValidationFunction]:
        pass
