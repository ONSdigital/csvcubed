"""
Pandas Utils
------------

This file provides additional utilities for pandas typoe commands
"""
import logging
from typing import Dict, List, Tuple

import pandas as pd

from pathlib import Path

from csvcubed.models.validationerror import ValidationError

from csvcubed.models.cube.validationerrors import DuplicateColumnTitleError

from .constants import ALL_RESERVED_COLUMN_NAMES, SPECIFIED_NA_VALUES

_logger = logging.getLogger(__name__)

def read_csv(csv_path: Path, **kwargs) -> Tuple[pd.DataFrame, List[ValidationError]]:
    """
    Read the csv as provided by the path csv_path into a pandas dataframe.

    Default behaviour is to assume it's a csv of observation data and to type
    cast any dimensions configured by convention as needed (dimensions are 
    type string). To disable this behaviour and load other csvs (for example
    a codelist) pass the keyword: is_obs_data = False. 

    :returns: a tuple of
        * pd.DataFrame (by default, Nan values are replace with empty strings)
        and (for observation data) dimension columns are cast to type "string".
        * list of ValidationErrors
    """

    # Unless specified otherwise, we assume we're loading observation data
    is_obs_data = kwargs.pop("is_obs_data", True)

    # Set default but allow interventions for advanced users
    if "keep_default_na" not in kwargs: kwargs["keep_default_na"] = False
    if "na_values" not in kwargs: kwargs["na_values"] = SPECIFIED_NA_VALUES

    df = pd.read_csv(csv_path, **kwargs)
    if not isinstance(df, pd.DataFrame):
        _logger.debug("Expected a pandas dataframe when reading from CSV, value was %s", df)
        raise ValueError(
            f"Expected a pandas dataframe when reading from CSV, value was {type(df)}"
        )

    if is_obs_data:

        dtype = kwargs.get("dtype", {})
        convertors = kwargs.get("convertors", {})
        for i, col in enumerate(df.columns.values):

            # If someone has passed in a value convertor for this column, leave it be
            # as a recast can silently change their expected output.
            if any([i in convertors, col in convertors]):
                continue

            # Don't alter a dataframe wide type declaration
            if dtype and not isinstance(dtype, dict):
                break

            if col not in dtype and col not in ALL_RESERVED_COLUMN_NAMES:
                if df[col].dtype != "string":
                    df[col] = df[col].astype("string")

    # Read first row as values rather than headers, so we can check for duplicate column titles
    col_title_counts = pd.read_csv(csv_path, header=None, nrows=1).iloc[0, :].value_counts()  # type: ignore
    duplicate_titles = list(col_title_counts[col_title_counts > 1].keys())

    return df, [
            DuplicateColumnTitleError(csv_column_title=dupe_title)
            for dupe_title in duplicate_titles
        ]


def kwargs_with_dimension_dtypes(config: Dict, **kwargs) -> Tuple[Dict, bool]:
    """
    Function that where given a cube config and the dict of keyword
    arguments intended for pandas, updates the keywords with the
    necessary datatypes.

    :returns: a tuple of
        Keyword arguments intended for use by the pandas read_csv function.
    """

    # No column config, return as is
    if "transform" not in config:
        return kwargs
    if "columns" in config["transform"]:
        return kwargs

    # If a user has explicitly declared column dtypes for
    # whatever reason, don't silently overwrite them.
    if "dtype" in kwargs:
        if isinstance(kwargs, dict):
            dimensions_with_explicit_dtypes = [x for x in kwargs["dype"]]
        else:
            # where the user is explicitly setting a constant dtype for
            # the whole dataframe, we'll have to trust they know what
            # they're doing.
            return kwargs

    # Dimensions which haven't had a pandas datatype declared are always type str.
    # This is necessary to stop pandas type assumptions altering outputs on the csv write,
    # by default a column of eg: ["04", "4"] would be assumed as numerical by pandas and
    # output as [4, 4]. In the context of a dimension 4 != 04
    
    columns_configs_with_type: Dict[str:Dict] = {
        column_label: column_config
        for column_label, column_config in config["transform"]["columns"].items()
        if "type" in column_config and column_label not in dimensions_with_explicit_dtypes
    }
    dimension_columns: List[str] = [
        column_label
        for column_label, column_config in columns_configs_with_type.items()
        if column_config["type"] == "dimension"
    ]

    # Columns without a type are also assumed to be a dimension
    # unless its a reserved column.
    dimension_columns += [
        column_label
        for column_label in config["transform"]["columns"]
        if all(
            column_label not in dimension_columns,
            column_label not in ALL_RESERVED_COLUMN_NAMES,
            column_label not in dimensions_with_explicit_dtypes)
    ]

    dtype = {column_label: "string" for column_label in dimension_columns}
    kwargs["dtype"] = dtype

    return kwargs