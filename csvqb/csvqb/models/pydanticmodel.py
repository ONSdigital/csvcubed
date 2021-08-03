import dataclasses
from dataclasses import dataclass, asdict, fields, is_dataclass
import pydantic
import pydantic.dataclasses
from pydantic import BaseConfig
from typing import ClassVar, Dict, Type, List, Iterable, Union
from abc import ABC


from .validationerror import ValidationError

_map_class_to_pydantic_constructor: ClassVar[Dict[Type, Type]] = dict()
"""_map_class_to_pydantic_constructor - Cache of pydantic constructor corresponding to a given class."""


@dataclass
class PydanticModel(ABC):
    """
    ValidatedModel - an abstract base class to be inherited by models which want a `validate` method which verifies
    that the model's attributes agree with the corresponding type annotations.
    Uses pydantic under the hood, but rather than using pydantic's constructor validation approach, we delay
    validation until the `validate` method is called.
    """

    class Config(BaseConfig):
        """pydantic Configuration - see https://pydantic-docs.helpmanual.io/usage/model_config/"""

        extra = "forbid"
        arbitrary_types_allowed = True
        validate_all = True

    @classmethod
    def _get_pydantic_constructor(cls) -> Type:
        if cls not in _map_class_to_pydantic_constructor:
            _map_class_to_pydantic_constructor[cls] = pydantic.dataclasses.dataclass(
                cls,
                config=PydanticModel.Config,
            )
        return _map_class_to_pydantic_constructor[cls]

    def as_dict(self) -> dict:
        """Use python dataclasses method to return this model as a dictionary."""
        return asdict(self)

    def _as_shallow_dict(self) -> dict:
        return dict([(f.name, getattr(self, f.name)) for f in fields(self)])

    def _to_pydantic_dataclass_or_validation_errors(
        self,
    ) -> Union[object, List[ValidationError]]:
        pydantic_class_constructor = self.__class__._get_pydantic_constructor()
        try:
            validated_model = pydantic_class_constructor(**self._as_shallow_dict())
        except pydantic.ValidationError as error:
            return [
                ValidationError(f"{self} - {e['loc']} - {e['msg']}")
                for e in error.errors()
            ]

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

                if value_does_not_contain_pydantic_dataclasses(field_value):
                    setattr(self, field.name, field_value)
            return []

        # Else we have validation errors
        return validated_model_or_errors


def value_does_not_contain_pydantic_dataclasses(value) -> bool:
    value_is_iterable = isinstance(value, Iterable) and not isinstance(value, str)
    if value_is_iterable:
        # Only copy iterables if all of their items can be copied.
        return all([value_does_not_contain_pydantic_dataclasses(v) for v in value])
    elif isinstance(value, object):
        # Don't copy object which have been cast to pydantic dataclasses
        cls = value.__class__
        return (not is_dataclass(cls)) or pydantic.dataclasses.is_builtin_dataclass(
            value.__class__
        )

    # Anything else should be fine.
    return True
