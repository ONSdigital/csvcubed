"""
Pandas Uitls
------------

This file provides additional utilities for pandas typoe commands
"""
import pandas as pd

from pathlib import Path

from csvcubed.models.cube.validationerrors import DuplicateColumnTitleError

specified_na_values = {
    "",
}


def read_csv(csv: Path, **kwargs) -> (pd.DataFrame, list):
    """
    :returns: a tuple of
        pd.DataFrame without the default na values being changes into NaN
        list of ValidationExceptions
    """
    df = pd.read_csv(csv, keep_default_na=False, na_values=specified_na_values, **kwargs)
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Expected a pandas dataframe when reading from CSV, value was {df}")

    # Read first row as values rather than headers, so we can check for duplicate column titles
    col_title_counts = pd.read_csv(csv, header=None, nrows=1).iloc[0, :].value_counts()
    duplicate_titles = list(col_title_counts[col_title_counts > 1].keys())
    if duplicate_titles:
        return df, [DuplicateColumnTitleError(csv_column_title=duplicate_titles[0])]

    return df, []
