import datetime
from dataclasses import dataclass, asdict, fields, is_dataclass
import pydantic
import pydantic.dataclasses
from pydantic import BaseConfig
from typing import ClassVar, Dict, Type, List, Iterable, Optional, Tuple
from abc import ABC


from .validationerror import ValidationError


@dataclass
class PydanticModel(ABC):
    """
    ValidatedModel - an abstract base class to be inherited by models which want a `validate` method which verifies
    that the model's attributes agree with the corresponding type annotations.
    Uses pydantic under the hood, but rather than using pydantic's constructor validation approach, we delay
    validation until the `validate` method is called.
    """

    _map_class_to_pydantic_constructor: ClassVar[Dict[Type, Type]] = dict()
    """_map_class_to_pydantic_constructor - Cache of pydantic constructor corresponding to a given class."""

    class Config(BaseConfig):
        """pydantic Configuration - see https://pydantic-docs.helpmanual.io/usage/model_config/"""

        extra = "forbid"
        arbitrary_types_allowed = True
        validate_all = True

    @classmethod
    def _get_pydantic_constructor(cls) -> Type:
        if cls not in PydanticModel._map_class_to_pydantic_constructor:
            new_cls = type(
                f"{cls.__name__}_pydanticmodel_{datetime.datetime.now().timestamp()}",
                (object,),
                dict([(f.name, f) for f in fields(cls)]),
            )

            # Annotations need to be built up from all base classes, but overridden as per inheritence.
            annotations = {}
            for c in reversed(cls.mro()):
                annotations_to_add = getattr(c, "__annotations__", {})
                annotations = dict(annotations, **annotations_to_add)

            setattr(new_cls, "__annotations__", annotations)
            PydanticModel._map_class_to_pydantic_constructor[
                cls
            ] = pydantic.dataclasses.dataclass(new_cls, config=PydanticModel.Config)
        return PydanticModel._map_class_to_pydantic_constructor[cls]

    def as_dict(self) -> dict:
        """Use python dataclasses method to return this model as a dictionary."""
        return asdict(self)

    def as_shallow_dict(self) -> dict:
        return dict([(f.name, getattr(self, f.name)) for f in fields(self)])

    def pydantic_validation(self) -> List[ValidationError]:
        """
        Validate this model using pydantic.
        Checks that all model attributes match the expected annotated data type. **Coerces values** where possible.
        """

        pydantic_class_constructor = self.__class__._get_pydantic_constructor()

        try:
            thingy = self.as_shallow_dict()
            validated_model = pydantic_class_constructor(**thingy)
        except pydantic.ValidationError as error:
            return [
                ValidationError(f"{self} - {e['loc']} - {e['msg']}")
                for e in error.errors()
            ]

        if validated_model is not None:
            #  Update this model's values with pydantic's coerced values
            for field in fields(self):
                field_value = getattr(validated_model, field.name)

                if value_does_not_contain_pydantic_dataclasses(field_value):
                    setattr(self, field.name, field_value)

        return []


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
