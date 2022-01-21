"""
Pandas
------

Functions to help when working with pandas dtypes.
"""
import json
from collections.abc import Iterable
from typing import DefaultDict, Union
from pandas import Series, DataFrame
from pandas.api.types import is_string_dtype
from warnings import warn

from csvcubed.models.cube.qb.components.validationerrors import (
    ReservedUriValueError,
    LabelUriCollisionError,
)
from csvcubed.models.validationerror import ValidationError
from csvcubed.utils.uri import uri_safe
from csvcubed.inputs import PandasDataTypes
from csvcubed.writers.urihelpers.skoscodelistconstants import SCHEMA_URI_IDENTIFIER


def uri_safe_ios(data: PandasDataTypes) -> dict[str, list[str]]:
    """
    Generate a dictionary of uri_safe values

    You must ensure that :obj:`data` represents categorical data where all
    categories are string types.
    """
    uri_safe_ios: dict[str, list[str]] = {}

    if data is not None:
        if isinstance(data, DataFrame):
            data = data.squeeze()
            if data is None:
                raise Exception("This should never happen.")
        assert isinstance(data, Series)

        original_safe_dict: dict[str, str] = {}

        for value in _get_unique_values(data):
            assert isinstance(value, str)
            original_safe_dict[value] = uri_safe(value)

        for original, safe in original_safe_dict.items():
            if original is None:
                raise Exception("This should also never happen.")
            # assert original is not None
            originals_list = uri_safe_ios.get(safe, [])
            originals_list.append(original)
            uri_safe_ios[safe] = originals_list

    return uri_safe_ios


def ensure_no_uri_safe_collision(
    data: Union[dict[str, list], PandasDataTypes], column_csv_title: str
) -> list[ValidationError]:
    """Validate that a categorical Pandas Series() has no uri_safe collisions
    (i.e. many values to one uri_safe result).

    You must ensure that :obj:`data` represents categorical data where all
    categories are string types.
    """
    uri_safe_ios_dict: Union[dict[str, list[str]], None]
    if isinstance(data, dict):
        uri_safe_ios_dict = data
    elif isinstance(data, (Series, DataFrame)) and _data_is_string_type(data):
        if isinstance(data, Series):
            uri_safe_ios_dict = uri_safe_ios(data)
        elif isinstance(data, DataFrame):
            uri_safe_ios_dict = uri_safe_ios(data)
    else:
        raise TypeError(
            f"Unexpected type: received {type(data)} expected pd.Series or dict"
        )
    errors = list()

    if uri_safe_ios_dict is None:
        return errors

    # Check for collisions, raise a Validation error
    for k, v in uri_safe_ios_dict.items():
        if len(v) > 1:
            errors.append(LabelUriCollisionError(column_csv_title, v, k))

    if SCHEMA_URI_IDENTIFIER in uri_safe_ios_dict:
        errors.append(
            ReservedUriValueError(
                column_csv_title,
                uri_safe_ios_dict[SCHEMA_URI_IDENTIFIER],
                SCHEMA_URI_IDENTIFIER,
            )
        )

    return errors


def coalesce_on_uri_safe(
    data: PandasDataTypes, column_csv_title: str
) -> PandasDataTypes:
    """Coalesce a categorical Pandas Series() or DataFrame so that all uri_safe collisions have the same value.
    The value which is preferred is the first value when the list of colliding category names are sorted()
    i.e. 'canada' and 'Canada' categories will replace 'canada' with 'Canada'
    """

    if data is None or not _data_is_string_type(data):
        return data
    else:

        uri_safe_ios_dict = uri_safe_ios(data)
        errors = ensure_no_uri_safe_collision(uri_safe_ios_dict, column_csv_title)
        non_recoverable_errors = [
            e for e in errors if not isinstance(e, LabelUriCollisionError)
        ]

        if any(non_recoverable_errors):
            raise ValueError(
                f"Unrecoverable error(s) experienced: {non_recoverable_errors}."
            )
        elif not any(errors):
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


def _data_is_string_type(data: PandasDataTypes) -> bool:
    if data is None:
        return False

    if data.dtype == "category":
        return is_string_dtype(data.cat.categories)

    return is_string_dtype(data)


def _get_unique_values(data: Series) -> Iterable[str]:
    if data.dtype == "category":
        return data.cat.categories

    return data.unique()
