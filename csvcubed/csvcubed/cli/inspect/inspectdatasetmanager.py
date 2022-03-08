"""
Inspect Dataset Manager
-------------------

Collection of functions handling csv-related operations used in the inspect cli.
"""


import logging
from enum import Enum
from pathlib import Path
import pandas as pd
from pandas import DataFrame

from csvcubed.models.inspectdataframeresults import DatasetObservationsInfoResult
from csvcubed.utils.file import get_root_dir_level


_logger = logging.getLogger(__name__)


class DatasetUnitType(Enum):
    """
    The type of dataset unit.
    """

    SINGLE_UNIT = 0

    MULTI_UNIT = 1


def load_csv_to_dataframe(json_path: Path, csv_path: Path) -> DataFrame:
    """
    Loads the csv in given path to a Panda Dataframe.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DataFrame` - Dataframe of the csv.
    """

    try:
        dataset_path = json_path.parent / csv_path
        _logger.debug(f"Dataset path: {dataset_path.absolute()}")

        dataset = DataFrame(pd.read_csv(dataset_path))
        _logger.info("Successfully loaded csv into dataframe.")
        return dataset
    except Exception as ex:
        raise Exception("An error occured while loading csv into dataframe.") from ex


def get_dataset_observations_info(
    dataset: DataFrame,
) -> DatasetObservationsInfoResult:
    """
    Generates the `DatasetObservationsInfoResult` from the dataset.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetObservationsInfoResult`
    """
    return DatasetObservationsInfoResult(
        len(dataset.index),
        dataset.duplicated().sum(),
        dataset.head(n=10),
        dataset.tail(n=10),
    )


def get_dataset_val_counts_splitted(dataset: DataFrame) -> DataFrame:
    """
    TODO: Not yet implemented.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DataFrame` - TODO
    """
    count_data = [{"measure_1": 10, "unit_1": 10}]
    return pd.DataFrame(count_data)


def get_dataset_unit_type(dataset: DataFrame) -> DatasetUnitType:
    """
    TODO: Not yet implemented.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetUnitType` - TODO
    """
    return DatasetUnitType.SINGLE_UNIT


def extract_single_measure_from_dsd(dataset: DataFrame) -> str:
    """
    TODO: Not yet implemented.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `str` - TODO
    """
    return ""


def get_measure_column_from_csvw(dataset: DataFrame) -> str:
    """
    TODO: Not yet implemented.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `str` - TODO
    """
    return ""


def get_units_column_from_csvw(dataset: DataFrame) -> str:
    """
    TODO: Not yet implemented.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `str` - TODO
    """
    return ""


def get_single_unit_from_dsd(dataset: DataFrame) -> str:
    """
    TODO: Not yet implemented.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `str` - TODO
    """
    return ""