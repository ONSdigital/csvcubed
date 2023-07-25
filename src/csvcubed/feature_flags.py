"""
Feature flags
-------------
"""
import os

from csvcubed.utils.text import str_to_bool

ATTRIBUTE_VALUE_CODELISTS: bool = str_to_bool(
    os.environ.get("OUTPUT_ATTR_VAL_CODE_LISTS", "false")
)
