"""
Text Utilities
--------------

Utilities for text manipulation.
"""


from typing import Dict


def truncate(message: str, message_truncate_at: int) -> str:
    """Truncate a string to a given length. Adds an elipsis if truncation is performed."""
    if len(message) <= message_truncate_at:
        return message
    else:
        return message[:message_truncate_at] + "…"


# Mapping of strings to bools for str_to_bool function to work
valid_bool_values: Dict[str, bool] = {
    "true": True,
    "1": True,
    "false": False,
    "0": False,
}


def str_to_bool(str_val: str, default: bool = False) -> bool:
    """Convert input strings to the correct boolean format in order to set environment variable value for feature flags"""
    return valid_bool_values.get(str_val.lower(), default)
