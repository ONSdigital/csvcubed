# This script contain a set of function that can be used to validate specific class attributes/ member variables
from csvcubed.models.validationerror import ValidateModelProperiesError

from typing import List, TypeVar, Type, Callable


T = TypeVar("T")


def validate_list(
    validate_list_item: Callable[[T], List[ValidateModelProperiesError]],
) -> Callable[[List[T], str], List[ValidateModelProperiesError]]:
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
    if not isinstance(value, str):
        return [
            ValidateModelProperiesError(
                "This variable should be a string value, check the following variable:",
                property_name,
            )
        ]

    return []


def validate_int_type(
    value: int, property_name: str
) -> List[ValidateModelProperiesError]:
    if not isinstance(value, int):
        return [
            ValidateModelProperiesError(
                "This variable should be a integer value, check the following variable:",
                property_name,
            )
        ]

    return []


from typing import Optional


def validate_optional(
    validate_item: Callable[[T, str], List[ValidateModelProperiesError]]
) -> Callable[[Optional[T], str], List[ValidateModelProperiesError]]:
    def _validate(
        maybe_item: Optional[T], property_name: str
    ) -> List[ValidateModelProperiesError]:
        if maybe_item is None:
            return []

        return validate_item(maybe_item, property_name)

    return _validate
