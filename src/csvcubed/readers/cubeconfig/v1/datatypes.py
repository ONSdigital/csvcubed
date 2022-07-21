import logging
from typing import Dict, List, Optional
from pathlib import Path

import pandas as pd

import csvcubed.readers.cubeconfig.v1.columnschema as schema
from csvcubed.readers.cubeconfig.v1.mapcolumntocomponent import (
    _from_column_dict_to_schema_model, schema
)
from .constants import CONVENTION_NAMES, PANDAS_DTYPE_MAPPING
_logger = logging.getLogger(__name__)


def _is_measures_column(column_label: str):
    return column_label in CONVENTION_NAMES["measures"]


def _is_observations_column(column_label: str):
    return column_label in CONVENTION_NAMES["observations"]


def _is_units_column(column_label: str):
    return column_label in CONVENTION_NAMES["units"]


def pandas_dtypes_from_columns_config(
    columns_config: Dict[str, dict]
) -> Dict[str, str]:
    """
    Given a dictionary of column config in the form:

    "Column Name": {
        <COLUMN CONFIG DICT>
    }

    Returns a dictionary mapping column names to pandas
    datatypes (which are decalred via strings).
    """

    dtype = {}
    for column_label, column_dict in columns_config.items():
        known_schema: schema.SchemaBaseClass = _from_column_dict_to_schema_model(
            column_label, column_dict
        )
        dtype[column_label] = pandas_dtype_from_schema(known_schema)

    return dtype


def pandas_dtype_from_schema(known_schema: schema.SchemaBaseClass) -> str:
    """
    Given a schema, return the appropriate pandas datatype
    """

    if isinstance(
        known_schema,
        (
            schema.NewDimension,
            schema.ExistingDimension,
            schema.NewMeasures,
            schema.ExistingMeasures,
            schema.NewUnits,
            schema.ExistingUnits,
            schema.NewAttributeResource,
            schema.ExistingAttributeResource,
        ),
    ):
        return "string"
    if isinstance(
        known_schema,
        (
            schema.NewAttributeLiteral,
            schema.ExistingAttributeLiteral,
            schema.ObservationValue,
        ),
    ):
        return PANDAS_DTYPE_MAPPING[known_schema.data_type]

    raise NotImplementedError(f"No handling for: {known_schema}")

def get_pandas_datatypes(
    csv_path: Path, config: Optional[dict] = None
) -> Dict[str, str]:
    """
    Creates a dictionary of column_label:datatype for all columns in
    the dataframe.
    """

    # Columns defined by explicit configuration
    dtype = {}
    if config:
        if "columns" in config:
            dtype = pandas_dtypes_from_columns_config(config["columns"])

    # Column configured by convention
    column_list: List[str] = pd.read_csv(csv_path, nrows=0).columns.tolist() # type: ignore
    untyped_column_list: List[str] = [x for x in column_list if x not in dtype.keys()]
    for uc in untyped_column_list:
        if _is_measures_column(uc.lower()):
            dtype[uc] = PANDAS_DTYPE_MAPPING["string"]
        if _is_units_column(uc.lower()):
            dtype[uc] = PANDAS_DTYPE_MAPPING["string"]
        if _is_observations_column(uc.lower()):
            dtype[uc] = PANDAS_DTYPE_MAPPING["decimal"]
        else:
            dtype[uc] = PANDAS_DTYPE_MAPPING["string"]

    return dtype
