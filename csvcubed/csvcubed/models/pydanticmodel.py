"""
Pydantic Model
--------------

The functionality necessary to repurpose pydantic so that we can validate at a point in time of our choosing.
"""

import dataclasses
from dataclasses import dataclass, fields, is_dataclass
import pydantic
import pydantic.dataclasses
from pydantic import BaseConfig, Extra
from typing import Dict, Type, List, Iterable, Union, Any
from abc import ABC

from csvcubedmodels.dataclassbase import DataClassBase

from .validationerror import (
    ValidationError,
    PydanticValidationError,
    UnknownPydanticValidationError,
    PydanticThrowableSpecificValidationError,
)

_map_class_to_pydantic_constructor: Dict[Type, Type] = dict()
"""_map_class_to_pydantic_constructor - Cache of pydantic constructor corresponding to a given class."""


@dataclass
class PydanticModel(DataClassBase, ABC):
    """
    ValidatedModel - an abstract base class to be inherited by models which want a `validate` method which verifies
    that the model's attributes agree with the corresponding type annotations.
    Uses pydantic under the hood, but rather than using pydantic's constructor validation approach, we delay
    validation until the `validate` method is called.
    """

    class _DefaultConfig(BaseConfig):
        """pydantic Configuration - see https://pydantic-docs.helpmanual.io/usage/model_config/"""

        extra = Extra.forbid
        arbitrary_types_allowed = True
        validate_all = True

    @classmethod
    def _get_pydantic_constructor(cls) -> Type:
        """Returns a constructor for creating an instance of this model which is a *pydantic* dataclass."""
        if cls not in _map_class_to_pydantic_constructor:
            _map_class_to_pydantic_constructor[cls] = pydantic.dataclasses.dataclass(
                cls,
                config=getattr(PydanticModel, "Config", PydanticModel._DefaultConfig),
            )
        return _map_class_to_pydantic_constructor[cls]

    def _to_pydantic_dataclass_or_validation_errors(
        self,
    ) -> Union[object, List[ValidationError]]:
        """
        Converts this model to a pydantic dataclass. Captures any validation errors in the process.

        Returns: Either a pydantic dataclass is validation was successful **OTHERWISE** it returns a list of errors.
        """
        pydantic_class_constructor = self.__class__._get_pydantic_constructor()
        try:
            validated_model = pydantic_class_constructor(**self._as_shallow_dict())
        except pydantic.ValidationError as error:
            errors = _extract_pydantic_underlying_errors(error)
            return errors

        return validated_model

    def pydantic_validation(self) -> List[ValidationError]:
        """
        Validate this model using pydantic.

        Checks that all model attributes match the expected annotated data type. **Coerces values** where possible.
        """
        validated_model_or_errors = self._to_pydantic_dataclass_or_validation_errors()
        if dataclasses.is_dataclass(validated_model_or_errors):
            validated_model = validated_model_or_errors
            #  Update this model's values with pydantic's coerced values
            for field in fields(self):
                field_value = getattr(validated_model, field.name)

                if not _value_is_list_of_or_single_pydantic_dataclass(field_value):
                    # Don't copy objects which have been cast to pydantic dataclasses
                    # They will bring their validation functionality with them.
                    setattr(self, field.name, field_value)
            return []
        else:
            assert isinstance(validated_model_or_errors, list)
            # Else we have validation errors
            return validated_model_or_errors


def _value_is_list_of_or_single_pydantic_dataclass(value: Any) -> bool:
    """
    Informs the caller whether the given `value` is a pydantic dataclass, or if it is a list of pydantic dataclasses.
    """
    value_is_iterable = isinstance(value, Iterable) and not isinstance(value, str)
    if value_is_iterable:
        # Only copy iterables if all of their items can be copied.
        return any([_value_is_list_of_or_single_pydantic_dataclass(v) for v in value])
    elif isinstance(value, object):
        cls = value.__class__
        return is_dataclass(cls) and (
            not pydantic.dataclasses.is_builtin_dataclass(cls)
        )

    # Anything else should be fine.
    return False


def _extract_pydantic_underlying_errors(
    error: Union[
        list,
        pydantic.error_wrappers.ValidationError,
        pydantic.error_wrappers.ErrorWrapper,
        Exception,
    ],
    path: List[str] = [],
) -> List[PydanticValidationError]:
    """
    Extracts the underlying ValueErrors which caused pydantic to raise an exception.

    Rather than keeping them hidden in the depths of objects with only strings hinting at what happened, we extract
    the underlying causes here in a list.
    """
    if isinstance(error, list):
        leaf_errors = []
        for item in error:
            leaf_errors += _extract_pydantic_underlying_errors(item, path)

        return leaf_errors
    elif isinstance(error, pydantic.error_wrappers.ErrorWrapper):
        location = error.loc_tuple()
        if len(location) == 1:
            # Just because I don't think we want a tuple of one item confusing the path with unnecessary
            # parentheses & commas.
            location = location[0]

        new_path = path + [str(location)]
        return _extract_pydantic_underlying_errors(error.exc, new_path)
    elif isinstance(error, pydantic.error_wrappers.ValidationError):
        return _extract_pydantic_underlying_errors(list(error.raw_errors), path)
    elif isinstance(error, PydanticThrowableSpecificValidationError):
        error.path = path
        return [error]
    else:
        return [UnknownPydanticValidationError(str(error), path, error)]
