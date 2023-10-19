"""
Pandas Utils
------------

This file provides additional utilities for pandas type commands
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union

import pandas as pd
from numpy import dtype

from csvcubed.models.cube.validationerrors import DuplicateColumnTitleError
from csvcubed.models.validationerror import ValidationError

_logger = logging.getLogger(__name__)

# Values used in place of NA in dataframe reads
specified_na_values = [
    "",
]


def read_csv(
    csv_path_or_url: Union[Path, str],
    keep_default_na: bool = False,
    na_values: list[str] = specified_na_values,
    dtype: Optional[Dict] = None,
    usecols: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, List[ValidationError]]:
    """
    :returns: a tuple of
        pd.DataFrame without the default na values being changes into NaN
        list of ValidationExceptions
    """

    df = pd.read_csv(
        csv_path_or_url,
        keep_default_na=keep_default_na,
        na_values=na_values,
        dtype=dtype,
        usecols=usecols,
    )
    if not isinstance(df, pd.DataFrame):
        _logger.debug(
            "Expected a pandas dataframe when reading from CSV, value was %s", df
        )
        raise ValueError(
            f"Expected a pandas dataframe when reading from CSV, value was {type(df)}"
        )

    # Read first row as values rather than headers, so we can check for duplicate column titles
    col_title_counts = pd.read_csv(csv_path_or_url, header=None, nrows=1).iloc[0, :].value_counts()  # type: ignore
    duplicate_titles = list(col_title_counts[col_title_counts > 1].keys())

    return df, [
        DuplicateColumnTitleError(csv_column_title=dupe_title)
        for dupe_title in duplicate_titles
    ]
