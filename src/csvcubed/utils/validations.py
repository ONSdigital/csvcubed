# This script contain a set of function that can be used to validate specific class attributes/ member variables
from typing import Callable, List, Optional, TypeVar

from csvcubed.models.validationerror import ValidateModelProperiesError
from csvcubed.utils.uri import looks_like_uri

T = TypeVar("T")


def validate_list(
    validate_list_item: Callable[[T, str], List[ValidateModelProperiesError]],
) -> Callable[[List[T], str], List[ValidateModelProperiesError]]:
    """
    This function will validate if the argument provided is in fact a list and,
    in a loop will check each member of the list and returns any errors returned by the item validation function.
    """

    def _validate(
        list_items: List[T], property_name: str
    ) -> List[ValidateModelProperiesError]:
        if not isinstance(list_items, list):
            return [
                ValidateModelProperiesError(
                    f"This variable should be a list, check the following variable:",
                    property_name,
                )
            ]

        return [
            err
            for list_item in list_items
            for err in validate_list_item(list_item, property_name)
        ]

    return _validate


def validate_str_type(
    value: str, property_name: str
) -> List[ValidateModelProperiesError]:
    """
    This function will validate if the argument provided is in fact a string type and,
    returns any errors returned by the item validation function.
    """
    if not isinstance(value, str):
        return [
            ValidateModelProperiesError(
                "This variable should be a string value, check the following variable:",
                property_name,
            )
        ]

    return []


def validate_uri(value: str, property_name: str) -> List[ValidateModelProperiesError]:
    """
    This function will validate if the argument provided is in fact a string type and,
    check is the string contains a uri. Either checks fail it returns any errors returned by the item validation function.
    """
    errors = validate_str_type(value, property_name)
    if any(errors):
        return errors

    if not looks_like_uri(value):
        return [
            ValidateModelProperiesError(
                "This variable is not a valid uri.", property_name
            )
        ]

    return []


def validate_int_type(
    value: int, property_name: str
) -> List[ValidateModelProperiesError]:
    """
    This function will validate if the argument provided is in fact a integer type and,
    returns any errors returned by the item validation function.
    """
    if not isinstance(value, int):
        return [
            ValidateModelProperiesError(
                "This variable should be a integer value, check the following variable:",
                property_name,
            )
        ]

    return []


def validate_optional(
    validate_item: Callable[[T, str], List[ValidateModelProperiesError]]
) -> Callable[[Optional[T], str], List[ValidateModelProperiesError]]:
    """
    This function will validate if the Optional argument provided is a None value it will return an empty list,
    else it returns any errors returned by the item validation function .
    """

    def _validate(
        maybe_item: Optional[T], property_name: str
    ) -> List[ValidateModelProperiesError]:
        if maybe_item is None:
            return []

        return validate_item(maybe_item, property_name)

    return _validate
