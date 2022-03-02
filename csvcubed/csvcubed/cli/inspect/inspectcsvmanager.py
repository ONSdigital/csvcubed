"""
Inspect CSV Manager
-------------------

Collection of functions handling csv-related operations used in the inspect cli.
"""


from enum import Enum
from pathlib import Path

import pandas as pd
from pandas import DataFrame


class DatasetUnit(Enum):
    """
    The type of dataset unit.
    """

    SINGLE_UNIT = 0

    MULTI_UNIT = 1


def load_csv_to_dataframe(csv_path: Path) -> DataFrame:
    
    return DataFrame(pd.read_csv(csv_path))


def get_dataset_head(dataset: DataFrame, num_observations: int = 10) -> DataFrame:
    return dataset.head(num_observations)


def get_dataset_tail(dataset: DataFrame, num_observations: int = 10) -> DataFrame:
    return dataset.tail(num_observations)


def get_dataset_val_counts(dataset: DataFrame) -> DataFrame:
    count_data = [{"measure_1": 10, "unit_1": 10}]
    return pd.DataFrame(count_data)
