"""
Constants that are relevant to more than one qb component.
"""

# A mapping of accepted datatypes from their csvw representation
# to appropriate primitive pandas dtypes.
# Please see:
# - https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dtypes.html
# - https://numpy.org/doc/stable/reference/arrays.dtypes.html
# - https://www.w3.org/TR/2015/REC-tabular-metadata-20151217/#h-built-in-datatypes
ACCEPTED_DATATYPE_MAPPING = {
    "anyURI": "string",
    "boolean": "bool",
    "decimal": "float64",
    "integer": "Int64",
    "long": "long",
    "int": "Int64",
    "short": "short",
    "nonNegativeInteger": "UInt64",
    "positiveInteger": "UInt64",
    "unsignedLong": "UInt64",
    "unsignedInt": "UInt64",
    "unsignedShort": "UInt64",
    "nonPositiveInteger": "Int64",
    "negativeInteger": "Int64",
    "double": "double",
    "float": "float64",
    "string": "string",
    "language": "string",
    "date": "string",
    "dateTime": "string",
    "dateTimeStamp": "string",
    "time": "string",
    "number": "double",
}
