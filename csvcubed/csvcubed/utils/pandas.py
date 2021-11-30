"""
Pandas
------

Functions to help when working with pandas dtypes.
"""

from typing import DefaultDict, Optional, Union
import math
from pandas import Series, DataFrame
from pandas.api.types import is_string_dtype
from warnings import warn
import logging

from csvcubed.utils.uri import uri_safe
from csvcubed.inputs import PandasDataTypes


def uri_safe_ios(data: PandasDataTypes) -> Optional[dict[str, list[str]]]:
    """Generate a dictionary of uri_safe values and """
    uri_safe_ios = dict[str, list[str]]

    if data is not None:

        if isinstance(data, DataFrame):
            data = data.squeeze()
            if data is None:
                raise Exception("This should never happen.")
            return_to_dataframe = True
        elif isinstance(data, Series):
            return_to_dataframe = False

        for original, safe in {
            value: uri_safe(value)
            for value in data.unique()
            if not isinstance(value, float) or not math.isnan(value)
        }.items():
            uri_safe_ios.get(safe).append(original)

        return uri_safe_ios if not return_to_dataframe else data.to_frame()
    else:
        return None


def ensure_no_uri_safe_collision(
    data: Union[dict[str, list], PandasDataTypes], series_name: Optional[str]
) -> list[ValueError]:
    """Validate that a categorical Pandas Series() has no uri_safe collisions (i.e. many values to one uri_safe result)"""
    uri_safe_ios_dict: Union[dict[str, list[str]], None]
    if isinstance(data, dict):
        uri_safe_ios_dict = data
    elif isinstance(data, Series):
        uri_safe_ios_dict = uri_safe_ios(data)
        series_name = str(data.name)
    elif isinstance(data, DataFrame):
        uri_safe_ios_dict = uri_safe_ios(data)
    else:
        raise TypeError(
            "Unexpected type: received {type(data)} expected pd.Series or dict"
        )
    errors = list()

    if uri_safe_ios_dict is None:
        return

    # Check for collisions, raise a Validation error
    for k, v in uri_safe_ios_dict.items():
        if len(v) > 1:
            errors.append(
                ValueError(
                    f'Labels "{v}" collide as single uri-safe value "{k}" in Series "{series_name}"'
                )
            )

    return errors


def coalesce_on_uri_safe(data: PandasDataTypes) -> PandasDataTypes:
    """Coalesce a categorical Pandas Series() or DataFrame so that all uri_safe collisions have the same value.
    The value which is preferred is the first value when the list of colliding category names are sorted()
    i.e. 'canada' and 'Canada' categories will replace 'canada' with 'Canada'
    """

    if not is_string_dtype(data.cat.categories) or data is None:
        return data

    uri_safe_ios_dict = uri_safe_ios(data)
    if (
        len(ensure_no_uri_safe_collision(uri_safe_ios_dict, series_name=str(data.name)))
        == 0
    ):
        # There is a 1:1 relationship between categories and uri_safe categoies
        return data
    else:

        cat_map = DefaultDict(str)

        for k, v in uri_safe_ios_dict.items():
            if len(v) > 1:
                warn(
                    message=f'Labels "{v}" collide as single uri-safe value "{k}" in column "{data.name}" and were consolidated'
                )

            for f in v:
                cat_map[f] = sorted(v)[0]

    return data.map(cat_map).astype("category")
