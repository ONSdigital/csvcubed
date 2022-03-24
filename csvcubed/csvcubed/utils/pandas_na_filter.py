import pandas as pd

from pathlib import Path

def refiltered_pandas_read_csv(csv: Path) ->  pd.DataFrame:

    specified_na_values = _get_new_na_values()
    df = pd.read_csv(csv, keep_default_na = False, na_values = specified_na_values)

    return df

def _get_new_na_values():
    specified_na_values = {
    "",
    "NaN"
    }
    return specified_na_values