from os import linesep
from typing import Dict, List
from attr import asdict

import pandas as pd


def get_printable_list_str(items: List) -> str:
    """
    Converts the given list of items into a printable string representation:
        -- Item 1
        -- Item 2

    Member of :file:`./utils/printable`.

    :return: `str` - string representation of the given list
    """
    if len(items) == 0 or len(items[0]) == 0:
        return "None"

    output_str = ""
    for item in items:
        output_str = f"{output_str}{linesep}\t\t-- {item}"
    return output_str


def get_printable_tabular_list_str(items: List) -> str:
    """
    Converts the given list of items into a printable list that can be a cell in tabular:
        |Item 1, Item 2|

    Member of :file:`./utils/printable`.

    :return: `str` - string representation of the given list
    """
    if len(items) == 0 or len(items[0]) == 0:
        return "None"

    output_str = ""
    for idx, item in enumerate(items):
        output_str = f"{output_str}{item}{',' if idx != len(items)-1 else ''}"
    return output_str


def get_printable_tabular_str(items: List[Dict], column_names=None) -> str:
    """
    Converts the given list of items of {key, value} into a printable tabular:
        |Key 1 | Key 2|
        |Val 1 | Val 2|

    Member of :file:`./utils/printable`.

    :return: `str` - string representation of the given list
    """
    if len(items) == 0:
        return "None"

    df = pd.DataFrame(items)
    if column_names:
        df.columns = column_names
    output_str = df.to_string(index=False)
    if output_str:
        return output_str
    raise Exception("Failed to convert data frame to string")
