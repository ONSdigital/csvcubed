"""
Constants relevant to loading v1 schema data
"""

# Reserved column titles that we use for the configuration via convention approach.
CONVENTION_NAMES = {
    "measures": {
        "measure",
        "measures",
        "measures column",
        "measure column",
        "measure type",
        "measure types",
    },
    "observations": {
        "observation",
        "observations",
        "obs",
        "values",
        "value",
        "val",
        "vals",
    },
    "units": {
        "unit",
        "units",
        "units column",
        "unit column",
        "unit type",
        "unit types",
    },
}


# Translation for csvw data types into equivilent pandas datatype
# Please see:
# - https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dtypes.html
# - https://numpy.org/doc/stable/reference/arrays.dtypes.html
PANDAS_DTYPE_MAPPING = {
    "anyURI": "string",
    "boolean": "bool",
    "date": "datetime64[ns]",
    "dateTime": "datetime64[ns]",
    "dateTimeStamp": "string",
    "decimal": "float64",
    "integer": "int64",
    "long": "long",
    "int": "int64",
    "short": "short",
    "nonNegativeInteger": "int64",
    "positiveInteger": "int64",
    "unsignedLong": "uint64",
    "unsignedInt": "uint64",
    "unsignedShort": "uint64",
    "nonPositiveInteger": "int64",
    "negativeInteger": "int64",
    "double": "double",
    "float": "float64",
    "string": "string",
    "language": "string",
    "time": "datetime64[ns]",
}
