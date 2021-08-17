"""
Pandas Inputs
-------------
"""
from typing import Union, Iterable, Optional, Any, List
import pandas as pd


PandasDataTypes = Union[pd.DataFrame, pd.Series, None]


def pandas_input_to_columnar(
    maybe_columnar_data: PandasDataTypes, allow_none: bool = True
) -> Optional[pd.Series]:
    if maybe_columnar_data is None:
        if allow_none:
            return None
        else:
            raise Exception("Columnar data not provided.")
    elif len(maybe_columnar_data.shape) != 1:
        raise Exception(
            f"Input data has shape {maybe_columnar_data.shape}. A single column of data must be provided."
        )
    if isinstance(maybe_columnar_data, pd.Series):
        return maybe_columnar_data

    return pd.Series(maybe_columnar_data)


def pandas_input_to_columnar_list(
    maybe_columnar_data: PandasDataTypes, allow_none: bool = True
) -> List[Any]:
    series = pandas_input_to_columnar(maybe_columnar_data, allow_none)
    if series is None:
        return []

    return series.tolist()


def pandas_input_to_columnar_str(
    maybe_columnar_data: PandasDataTypes, allow_none: bool = True
) -> Iterable[str]:
    series = pandas_input_to_columnar(maybe_columnar_data, allow_none)
    if series is None:
        return []

    return [str(d) for d in series.tolist()]
