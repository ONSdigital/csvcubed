"""
Pandas Inputs
-------------
"""
from typing import Union, Iterable, Optional, Any, List
import pandas as pd


PandasDataTypes = Union[pd.DataFrame, pd.Series, None]


def pandas_input_to_columnar(
    maybe_columnar_data: PandasDataTypes, allow_no_data_at_all: bool = True
) -> Optional[pd.Series]:
    if maybe_columnar_data is None:
        if allow_no_data_at_all:
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
    maybe_columnar_data: PandasDataTypes, allow_no_data_at_all: bool = True
) -> List[Any]:
    series = pandas_input_to_columnar(maybe_columnar_data, allow_no_data_at_all)
    if series is None:
        return []

    return series.tolist()


def pandas_input_to_columnar_optional_str(
    maybe_columnar_data: PandasDataTypes,
    allow_no_data_at_all: bool = True,
) -> Iterable[Optional[str]]:
    series = pandas_input_to_columnar(maybe_columnar_data, allow_no_data_at_all)
    if series is None:
        return []

    return [None if pd.isna(d) else str(d) for d in series.tolist()]


def pandas_input_to_columnar_str(
    maybe_columnar_data: PandasDataTypes,
    allow_no_data_at_all: bool = True,
) -> Iterable[str]:
    """
    Convert pandas data to an iterable of strings. Ensure no values are missing.

    :return: A generator checking that no values are :obj:`None`
    :raise ValueError: when a value is missing.
    """
    for value in pandas_input_to_columnar_optional_str(
        maybe_columnar_data, allow_no_data_at_all
    ):
        if value is None:
            raise ValueError("Missing value found in data.")
        yield value
