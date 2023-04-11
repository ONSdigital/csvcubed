# This script contain a set of function that can be used to validate specific class attributes/ member variables
import builtins
import datetime as dt
from enum import Enum
from math import isinf, isnan
from pathlib import Path
from typing import Any, Callable, List, Optional, Type, TypeVar

from csvcubed.models.cube.qb.components.constants import ACCEPTED_DATATYPE_MAPPING
from csvcubed.models.validatedmodel import ValidatedModel, ValidationFunction
from csvcubed.models.validationerror import ValidateModelPropertiesError
from csvcubed.utils.text import truncate
from csvcubed.utils.uri import looks_like_uri

T = TypeVar("T")


def list(
    validate_list_item: Callable[[T, List[str]], List[ValidateModelPropertiesError]],
) -> Callable[[List[T], List[str]], List[ValidateModelPropertiesError]]:
    """
    This function will validate if the argument provided is in fact a list and,
    in a loop will check each member of the list and returns any errors returned by the item validation function.
    """

    def _validate(
        list_items: List[T], property_path: List[str]
    ) -> List[ValidateModelPropertiesError]:
        if not isinstance(list_items, builtins.list):
            return [
                ValidateModelPropertiesError(
                    f"The value '{truncate(str(list_items), 50)}' should be a list.",
                    property_path,
                    list_items,
                )
            ]

        return [
            err
            for i, list_item in enumerate(list_items)
            for err in validate_list_item(list_item, [*property_path, str(i)])
        ]

    return _validate


def string(value: str, property_path: List[str]) -> List[ValidateModelPropertiesError]:
    """
    This function will validate if the argument provided is in fact a string type and,
    returns any errors returned by the item validation function.
    """
    if not isinstance(value, str):
        return [
            ValidateModelPropertiesError(
                f"The value '{truncate(str(value), 50)}' should be a string.",
                property_path,
                value,
            )
        ]

    return []


def uri(value: str, property_path: List[str]) -> List[ValidateModelPropertiesError]:
    """
    This function will validate if the argument provided is in fact a string type and,
    check is the string contains a uri. Either checks fail it returns any errors returned by the item validation function.
    """
    errors = string(value, property_path)
    if any(errors):
        return errors

    if not looks_like_uri(value):
        return [
            ValidateModelPropertiesError(
                f"The value '{truncate(str(value), 50)}' should be a URI.",
                property_path,
                value,
            )
        ]

    return []


def integer(value: int, property_path: List[str]) -> List[ValidateModelPropertiesError]:
    """
    This function will validate if the argument provided is in fact a integer type and,
    returns any errors returned by the item validation function.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        return [
            ValidateModelPropertiesError(
                f"The value '{truncate(str(value), 50)}' should be an integer.",
                property_path,
                value,
            )
        ]

    return []


def boolean(
    value: bool, property_path: List[str]
) -> List[ValidateModelPropertiesError]:
    """
    This function will validate if the argument provided is in fact a boolean type and,
    returns and error if it isn't.
    """
    if not isinstance(value, bool):
        return [
            ValidateModelPropertiesError(
                f"This value '{truncate(str(value), 50)}' should be a boolean value.",
                property_path,
                value,
            )
        ]

    return []


def optional(
    validate_item: Callable[[T, List[str]], List[ValidateModelPropertiesError]]
) -> Callable[[Optional[T], List[str]], List[ValidateModelPropertiesError]]:
    """
    This function will validate if the Optional argument provided is a None value it will return an empty list,
    else it returns any errors returned by the item validation function .
    """

    def _validate(
        maybe_item: Optional[T], property_path: List[str]
    ) -> List[ValidateModelPropertiesError]:
        if maybe_item is None:
            return []

        return validate_item(maybe_item, property_path)

    return _validate


def float(
    value: builtins.float, property_path: List[str]
) -> List[ValidateModelPropertiesError]:
    """
    This function will validate if the argument provided is in fact a float type and,
    returns any errors returned by the item validation function.
    """
    if not isinstance(value, builtins.float):
        return [
            ValidateModelPropertiesError(
                f"The value '{truncate(str(value), 50)}' should be a float.",
                property_path,
                value,
            )
        ]
    elif isnan(value):
        return [
            ValidateModelPropertiesError(
                "The value should be a float but is Not a Number (NaN).",
                property_path,
                value,
            )
        ]
    elif isinf(value):
        return [
            ValidateModelPropertiesError(
                "The value should be a float but is ±infinity.",
                property_path,
                value,
            )
        ]

    return []


def file(value: Path, property_path: List[str]) -> List[ValidateModelPropertiesError]:
    """
    This function validates whether the given argument is in fact of type Path, and if not,
    returns any validation errors raised by the validation function.
    """
    if isinstance(value, Path):
        if not value.exists():
            return [
                ValidateModelPropertiesError(
                    f"The file '{truncate(str(value), 50)}' does not exist.",
                    property_path,
                    value,
                )
            ]
        else:
            return []
    else:
        return [
            ValidateModelPropertiesError(
                f"The file '{truncate(str(value), 50)}' is not a valid file path.",
                property_path,
                value,
            )
        ]


def any_of(*conditions: ValidationFunction) -> ValidationFunction:
    """
    This function will validate if the argument provided is an instance of any of the types
    specified. (Useful for Unions.) Returns any errors returned by the validation function.
    """

    def validate(
        value: Any, property_path: List[str]
    ) -> List[ValidateModelPropertiesError]:
        all_errors = []
        for condition in conditions:
            errs = condition(value, property_path)
            if not any(errs):
                return []
            all_errors += errs

        return [
            ValidateModelPropertiesError(
                f"The value '{truncate(str(value), 50)}' does not satisfy any single condition for the variable.",
                property_path,
                value,
            ),
            *all_errors,
        ]

    return validate


def all_of(*conditions: ValidationFunction) -> ValidationFunction:
    """
    This function will validates that the property matches all of the conditions
    specified. Returns any errors returned by the validation function.
    """

    def validate(
        value: Any, property_path: List[str]
    ) -> List[ValidateModelPropertiesError]:
        all_errors = []
        for condition in conditions:
            errors = condition(value, property_path)
            if any(errors):
                all_errors += errors

        return all_errors

    return validate


def enum(enum_type: Type[Enum]) -> ValidationFunction:
    """
    This function will validate if the argument provided is in fact an enum type and,
    returns any errors returned by the validation function.
    """

    def validate(
        value: Any, property_path: List[str]
    ) -> List[ValidateModelPropertiesError]:
        for enum_value in enum_type:
            if value == enum_value:
                return []

        return [
            ValidateModelPropertiesError(
                f"Could not find matching enum value for '{truncate(str(value), 50)}' in {enum_type.__name__}.",
                property_path,
                value,
            )
        ]

    return validate


def data_type(
    data_type: str, property_path: List[str]
) -> List[ValidateModelPropertiesError]:
    """
    This function will validate if the argument provided is a member of the accepted data types,
    and returns any errors that are raised.
    """
    if data_type not in ACCEPTED_DATATYPE_MAPPING.keys():
        return [
            ValidateModelPropertiesError(
                f"'{truncate(str(data_type), 50)}' is not recognised as a valid data type.",
                property_path,
                data_type,
            )
        ]
    return []


def validated_model(validated_model_type: Type[ValidatedModel]):
    """
    Performs the standard validation of any object which inherits from ValidatedModel.

    This saves us from having to write a validation function for each class which
    implements/inherits from ValidatedModel.
    """

    if not issubclass(validated_model_type, ValidatedModel):
        # This error is really for developers when running tests.
        raise TypeError(
            f"Type '{validated_model_type}' is not an instance of {ValidatedModel.__name__}."
            f"This function is only designed to work with types which extend {ValidatedModel.__name__}."
        )

    def validate(
        value: ValidatedModel, property_path: List[str]
    ) -> List[ValidateModelPropertiesError]:
        if not isinstance(value, validated_model_type):
            # This error occurs when runtime validation occurs.
            return [
                ValidateModelPropertiesError(
                    f"Value '{truncate(str(value), 50)}' was not an instance of the expected type '{validated_model_type.__name__}'.",
                    property_path,
                    value,
                )
            ]

        return value.validate(property_path=property_path)

    return validate


def is_instance_of(expect_instance_type: Type[object]) -> ValidationFunction:
    """
    Validation function that can apply type validation to class properties in a generic manner,
    by specifying what instance/type of object to expect. This saves effort from having to create
    custom validation functions for specific types that do not inherit from ValidatedModel.
    """

    def _validate(
        value: Any, property_path: List[str]
    ) -> List[ValidateModelPropertiesError]:
        if not isinstance(value, expect_instance_type):
            return [
                ValidateModelPropertiesError(
                    f"Value '{truncate(str(value), 50)}' was not an instance of the expected type '{expect_instance_type.__name__}'.",
                    property_path,
                    value,
                ),
            ]
        return []

    return _validate
