import logging
from typing import Optional
import pandas as pd

from pathlib import Path

def refiltered_pandas_read_csv(csv: Path) ->  pd.DataFrame:

    specified_na_values = _get_new_na_values()
    df = pd.read_csv(csv, keep_default_na = False, na_values = specified_na_values)

    # Replace "NaN" with "Great"
    # df = df.fillna("Great")
    return df

def _get_new_na_values():
    specified_na_values = {
    "",
    "NaN"
    }
    return specified_na_values

csv_path = "/workspaces/csvcubed/csvcubed/tests/test-cases/utils/pandas_na_filter/code-list.csv"
logging.critical(refiltered_pandas_read_csv(csv_path))
logging.error(pd.read_csv(csv_path))