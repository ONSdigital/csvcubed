"""
Constants in use by the configloader
note: Reserved column names taken from:
https://gss-cogs.github.io/csvcubed-docs/external/guides/configuration/convention/#conventional-column-names
"""

# Measure column names that are reserved
RESERVED_COLUMN_NAMES_MEASURE = ["Measure", "measures", "measures column", "measure column",
"measure type", "measure types"]

# Observation column names that are reserved
RESERVED_COLUMN_NAMES_OBSERVATION = ["Observations", "obs", "values", "value", "val", "vals"]

# Unit column names that are reserved
RESERVED_COLUMN_NAMES_UNIT = ["Unit", "units", "units column", "unit column", "units type", "unit type"]

# All reserved column names
ALL_RESERVED_COLUMN_NAMES = (
    RESERVED_COLUMN_NAMES_MEASURE + 
    RESERVED_COLUMN_NAMES_OBSERVATION +
    RESERVED_COLUMN_NAMES_UNIT
    )

# Values used in place of NA in dataframe reads
SPECIFIED_NA_VALUES = {
    "",
}