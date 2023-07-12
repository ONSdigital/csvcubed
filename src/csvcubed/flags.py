"""
Feature flags
-------------
"""
import os
from typing import Dict

valid_bool_values: Dict[str, bool] = {
    "true": True,
    "1": True,
    "false": False,
    "0": False,
}


def str_to_bool(str_val: str, default: bool = False) -> bool:
    return valid_bool_values.get(str_val.lower(), default)


ATTRIBUTE_VALUE_CODELISTS: bool = str_to_bool(
    os.environ.get("OUTPUT_ATTR_VAL_CODE_LISTS", "false")
)
