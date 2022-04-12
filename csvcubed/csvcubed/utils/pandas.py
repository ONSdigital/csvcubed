"""
Pandas Uitls
------------

This file provides additional utilities for pandas typoe commands
"""
import pandas as pd

from pathlib import Path

specified_na_values = {
"",
}

def read_csv(csv: Path, **kwargs) ->  pd.DataFrame:
    """
    :returns: pd.DataFrame without the default na values being changes into NaN

    """

    df = pd.read_csv(csv, keep_default_na = False, na_values = specified_na_values, **kwargs)
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Expected a pandas dataframe when reading from CSV, value was {df}")

    return df
