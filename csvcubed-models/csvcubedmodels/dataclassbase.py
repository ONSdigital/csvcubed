"""
DataClass Base
--------------

Provides some utilities to help with serialisation/deserialisation
"""
import copy
import datetime
import json
import typing
from abc import ABC
import collections.abc
from dataclasses import Field, _MISSING_TYPE, fields, asdict, dataclass
from typing import List, Any, get_type_hints, Dict, Set, Type


class DataClassFromDictValueError(ValueError):
    ...


_map_coercion_permitted: Dict[Type, Set[Type]] = {int: {float}}
"""Map of coercion directions permitted, value type => expected static type"""


def _type_coercion_permitted(value_data_type: Type, annotation_data_type: Type) -> bool:
    permitted_coercions = _map_coercion_permitted.get(value_data_type)
    return (
        permitted_coercions is not None and annotation_data_type in permitted_coercions
    )


TDataClassBase = typing.TypeVar("TDataClassBase", bound="DataClassBase")


@dataclass
class DataClassBase(ABC):
    """
    Provides functionality to go to/from dictionary or JSON representations of this class.

    N.B. This requires that all subclasses have the :obj:`@dataclass` attribute.
    """

    def as_dict(self) -> dict:
        """Use python dataclasses method to return this model as a dictionary."""
        return asdict(self)

    def as_json_dict(self) -> dict:
        """
        :return: a dict suitable for JSON serialisation containing a representation of this object.
        """
        d = replace_with_json_serialisable_types(self.as_dict())
        assert isinstance(d, dict)
        return d

    def as_json(self) -> str:
        """
        :return: the JSON serialisation containing a representation of this object.
        """
        return json.dumps(self.as_json_dict())

    def override_with(
        self: TDataClassBase,
        overriding_values: TDataClassBase,
        overriding_keys: typing.Optional[Set[str]] = None,
    ):
        """
        Allows you to override specific attributes of this instance with values from another instance.
        """
        if not isinstance(overriding_values, self.__class__):
            raise ValueError(
                f"overriding_values is not an instance of {self.__class__}"
            )

        for field in fields(self):
            if overriding_keys is not None and field.name not in overriding_keys:
                continue

            self_val = getattr(self, field.name)
            overriding_val = getattr(overriding_values, field.name)
            if self_val == overriding_val:
                continue

            setattr(self, field.name, overriding_val)

    @classmethod
    def dict_fields_match_class(cls: typing.Type, d: dict) -> bool:
        fields_in_class = fields(cls)
        field_defined_keys = {field.name for field in fields_in_class}

        required_fields: List[Field] = [
            f
            for f in fields_in_class
            if isinstance(f.default, _MISSING_TYPE)
            and isinstance(f.default_factory, _MISSING_TYPE)
        ]
        all_required_fields_present = all([f.name in d.keys() for f in required_fields])
        dict_keys_undefined_in_class = any(
            [k for k in d.keys() if k not in field_defined_keys]
        )

        return all_required_fields_present and not dict_keys_undefined_in_class

    @classmethod
    def from_json(cls: Type[TDataClassBase], j: str) -> TDataClassBase:
        d = json.loads(j)
        if not isinstance(d, dict):
            raise ValueError(
                f"Unhandled input JSON structure {type(d)}. Expected dictionary/map for {cls.__name__}"
            )

        return cls.from_dict(d)

    @classmethod
    def from_dict(cls: Type[TDataClassBase], d: dict) -> TDataClassBase:
        """
        Attempt to inflate an instance of this class from a dictionary of values using static type annotations as
        guides.

        N.B. this won't work in all cases. You should *really* test this against all of the classes you're expecting
        to be able to inflate.
        """

        all_fields: List[Field] = list(fields(cls))
        init_fields = [f for f in all_fields if f.init]
        non_init_fields = [f for f in all_fields if not f.init]

        type_hints = cls._get_type_hints()
        init_values = {}
        for field in init_fields:
            init_values[field.name] = cls._get_value_for_field(d, field, type_hints)

        instance = cls(**init_values)  # type: ignore

        for field in non_init_fields:
            field_value = cls._get_value_for_field(d, field, type_hints)
            setattr(instance, field.name, field_value)

        return instance

    @classmethod
    def _get_value_for_field(
        cls, dict_values: dict, field: Field, type_hints: Dict[str, Any]
    ) -> Any:
        if field.name in dict_values.keys():
            val = dict_values[field.name]
            typing_hint = type_hints.get(field.name)
            if typing_hint is not None:
                val = cls._get_value_for_typed_field(val, field, typing_hint)

            return val
        elif not isinstance(field.default, _MISSING_TYPE):
            return copy.deepcopy(field.default)
        elif not isinstance(field.default_factory, _MISSING_TYPE):
            return field.default_factory()
        else:
            raise DataClassFromDictValueError(
                f"Missing required field '{field.name}' on {cls}. Values provided: {dict_values}."
            )

    @classmethod
    def _get_value_for_typed_field(
        cls, val: Any, field: Field, typing_hint: Any
    ) -> Any:
        generic_type_args = typing.get_args(typing_hint)
        value_type = type(val)

        if value_type == typing_hint:
            return val
        elif (
            isinstance(val, dict)
            and isinstance(typing_hint, type)
            and issubclass(typing_hint, DataClassBase)
            and typing_hint.dict_fields_match_class(val)
        ):
            # recursive application of `from_dict`.
            return typing_hint.from_dict(val)
        elif len(generic_type_args) > 0:
            origin_type = typing.get_origin(typing_hint)
            if isinstance(origin_type, type) and issubclass(
                origin_type, collections.abc.Iterable
            ):
                return cls._get_value_for_generic_iterable_field(
                    field, typing_hint, origin_type, generic_type_args, val
                )
            elif origin_type == typing.Union:
                return cls._get_value_for_generic_union(
                    field, typing_hint, generic_type_args, val
                )
            else:
                raise DataClassFromDictValueError(
                    f"Unable to inflate generic type {typing_hint} from dictionary."
                )
        elif _type_coercion_permitted(value_type, typing_hint):
            try:
                return typing_hint(val)  # type: ignore
            except:
                ...
        elif isinstance(val, str) and issubclass(typing_hint, datetime.date):
            # ISO-8601 conversion.
            if issubclass(typing_hint, datetime.datetime):
                return datetime.datetime.fromisoformat(val)
            return datetime.date.fromisoformat(val)

        raise DataClassFromDictValueError(
            f"Could not match {val} with static type {typing_hint}"
        )

    @classmethod
    def _get_value_for_generic_iterable_field(
        cls,
        field: Field,
        typing_hint: Any,
        origin_type: Any,
        generic_type_args: collections.abc.Iterable,
        val: Any,
    ) -> Any:
        generic_type_args = list(generic_type_args)

        if not isinstance(val, collections.abc.Iterable):
            raise DataClassFromDictValueError(
                f"Unable to inflate {cls.__name__}.{field.name} as dictionary value is not list: {val}"
            )

        typing_args_contain_subclass_dataclassbase = cls._get_generic_type_args_subclassing_dataclassbase(
            generic_type_args
        )

        if len(typing_args_contain_subclass_dataclassbase) > 0:
            if len(generic_type_args) == 1:
                iterable_value_type = generic_type_args[0]
                mapped_child_values = [
                    cls._get_value_for_typed_field(v, field, iterable_value_type)
                    for v in val
                ]
                return origin_type(mapped_child_values)
            elif len(generic_type_args) > 1:
                raise DataClassFromDictValueError(
                    f"Unable to inflate generic type {typing_hint} from dictionary."
                )
        return val

    @classmethod
    def _get_generic_type_args_subclassing_dataclassbase(
        cls, generic_type_args: collections.abc.Iterable
    ) -> Set:
        args_subclassing_dataclassbase = {
            a
            for a in generic_type_args
            if isinstance(a, type) and issubclass(a, DataClassBase)
        }

        for a in generic_type_args:
            args = typing.get_args(a)
            # recursive search down the type tree to see if we can find anything subclassing DataClassBase.
            if len(cls._get_generic_type_args_subclassing_dataclassbase(args)) > 0:
                args_subclassing_dataclassbase.add(a)

        return args_subclassing_dataclassbase

    @classmethod
    def _get_value_for_generic_union(
        cls,
        field: Field,
        union_typing_hint: Any,
        generic_type_args: collections.abc.Iterable,
        val: Any,
    ) -> Any:
        for arg in generic_type_args:
            try:
                return cls._get_value_for_typed_field(val, field, arg)
            except DataClassFromDictValueError:
                pass

        raise DataClassFromDictValueError(
            f"Could not find matching type in union {union_typing_hint} to represent {val}"
        )

    def _as_shallow_dict(self) -> dict:
        """Returns a dictionary which is essentially a shallow copy of this dataclass."""
        return dict([(f.name, getattr(self, f.name)) for f in fields(self)])

    @classmethod
    def _get_type_hints(cls) -> dict:
        """
        Fetches type hints associated with this class.

        Ensures that overridden properties have their type hints overridden too.
        """
        type_hints = {}
        for c in reversed(cls.mro()):
            type_hints = dict(type_hints, **get_type_hints(c, include_extras=True))

        return type_hints


def replace_with_json_serialisable_types(val: Any) -> Any:
    """
    :return: A replacement of built-in types which are not JSON serialisable with ones which are.

    e.g. :obj:`~datetime.datetime` instances get replaced with ISO-8601 strings.

    Its inverse is :func:`replace_serialised_types_with_builtin_types`.
    """

    if isinstance(val, datetime.date):
        return val.isoformat()
    elif isinstance(val, dict):
        return dict(
            [
                (key, replace_with_json_serialisable_types(value))
                for key, value in val.items()
            ]
        )
    elif isinstance(val, list):
        return [replace_with_json_serialisable_types(item) for item in val]
    elif isinstance(val, type):
        return val.__name__

    return val
