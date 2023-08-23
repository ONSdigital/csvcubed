"""
Feature flags
-------------
"""
import os

from csvcubed.utils.text import str_to_bool

"""
When importing ATTRIBUTE_VALUE_CODELISTS, use `from csvcubed import feature_flags` *NOT* from `csvcubed.feature_flags import ATTRIBUTE_VALUE_CODELISTS`

To set the OUTPUT_ATTR_VAL_CODE_LISTS environmental variable in order to run `csvcubed build` and output attribute value codelists, run `export OUTPUT_ATTR_VAL_CODE_LISTS=1` or `OUTPUT_ATTR_VAL_CODE_LISTS=true`, then `csvcubed build <data.csv> -c <data.json>`

To revert, run `export OUTPUT_ATTR_VAL_CODE_LISTS=0` or `export OUTPUT_ATTR_VAL_CODE_LISTS=false`
"""
ATTRIBUTE_VALUE_CODELISTS: bool = str_to_bool(
    os.environ.get("OUTPUT_ATTR_VAL_CODE_LISTS", "false")
)
