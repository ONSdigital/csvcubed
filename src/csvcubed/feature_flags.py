"""
Feature flags
-------------
"""
import os

from csvcubed.utils.text import str_to_bool

# When importing ATTRIBUTE_VALUE_CODELISTS, use `from csvcubed import feature_flags` *NOT* from `csvcubed.feature_flags import ATTRIBUTE_VALUE_CODELISTS`
ATTRIBUTE_VALUE_CODELISTS: bool = str_to_bool(
    os.environ.get("OUTPUT_ATTR_VAL_CODE_LISTS", "true")
)
