# This script contain a set of function that can be used to validate specific class attributes/ member variables
from csvcubed.models.validationerror import ValidateModelProperiesError

from typing import List


def validate_list_of_str(
    value: List[str], property_name: str
) -> List[ValidateModelProperiesError]:
    is_valid = isinstance(value, list) and all(isinstance(v, str) for v in value)

    if not is_valid:
        return [
            ValidateModelProperiesError(
                "This variable should be a list of string values, check the following variable:",
                property_name,
            )
        ]

    return []


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
