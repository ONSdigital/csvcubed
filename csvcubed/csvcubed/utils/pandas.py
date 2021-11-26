"""
Pandas
------

Functions to help when working with pandas dtypes.
"""

from typing import DefaultDict, Optional, Union
import math
from pandas import Series
from pandas.api.types import is_string_dtype
from warnings import warn
import logging

from csvcubed.utils.uri import uri_safe


def uri_safe_ios(data: Series) -> dict[str, list[str]]:
    """Generate a dictionary of uri_safe values and """
    uri_safe_ios = DefaultDict()

    for original, safe in {
        value: uri_safe(value)
        for value in data.unique()
        if not isinstance(value, float) or not math.isnan(value)
    }.items():
        uri_safe_ios.setdefault(safe, []).append(original)

    return uri_safe_ios


def ensure_no_uri_safe_collision(
    data: Union[Series, dict[str, list[str]]], series_name: Optional[str]
) -> list[ValueError]:
    """Validate that a categorical Pandas Series() has no uri_safe collisions (i.e. many values to one uri_safe result)"""
    uri_safe_ios_dict: dict[str, list[str]]
    if isinstance(data, dict):
        uri_safe_ios_dict = data
    elif isinstance(data, Series):
        uri_safe_ios_dict = uri_safe_ios(data)
        series_name = str(data.name)
    else:
        raise TypeError(
            "Unexpected type: received {type(data)} expected pd.Series or dict"
        )
    errors = list()

    # Check for collisions, raise a Validation error
    for k, v in uri_safe_ios_dict.items():
        if len(v) > 1:
            errors.append(
                ValueError(
                    f'Labels "{v}" collide as single uri-safe value "{k}" in Series "{series_name}"'
                )
            )

    return errors


def coalesce_on_uri_safe(data: Series) -> Series:
    """Coalesce a categorical Pandas Series() so that all uri_safe collisions have the same value.
    The value which is preferred is the first value when the list of colliding category names are sorted()
    i.e. 'canada' and 'Canada' categories will replace 'canada' with 'Canada'
    """

    if not is_string_dtype(data.cat.categories):
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
