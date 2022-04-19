"""
Pandas Utils
------------

This file provides additional utilities for pandas typoe commands
"""
import logging
from typing import Tuple, List

import pandas as pd

from pathlib import Path

from csvcubed.models.validationerror import ValidationError

from csvcubed.models.cube.validationerrors import DuplicateColumnTitleError

specified_na_values = {
    "",
}

logger = logging.getLogger(__name__)

def read_csv(csv: Path, **kwargs) -> Tuple[pd.DataFrame, List[ValidationError]]:
    """
    :returns: a tuple of
        pd.DataFrame without the default na values being changes into NaN
        list of ValidationExceptions
    """
    df = pd.read_csv(
        csv, keep_default_na=False, na_values=specified_na_values, **kwargs
    )
    if not isinstance(df, pd.DataFrame):
        logger.debug("Expected a pandas dataframe when reading from CSV, value was %s", df)
        raise ValueError(
            f"Expected a pandas dataframe when reading from CSV, value was {type(df)}"
        )


    # Read first row as values rather than headers, so we can check for duplicate column titles
    col_title_counts = pd.read_csv(csv, header=None, nrows=1).iloc[0, :].value_counts()  # type: ignore
    duplicate_titles = list(col_title_counts[col_title_counts > 1].keys())
    if any(duplicate_titles):
        return df, [
            DuplicateColumnTitleError(csv_column_title=dupe_title)
            for dupe_title in duplicate_titles
        ]

    return df, []
