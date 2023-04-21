"""
Inspect Dataset Manager
-----------------------

Collection of functions handling csv-related operations used in the inspect cli.
"""


import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from csvcubed.cli.error_mapping import friendly_error_mapping
from csvcubed.models.csvcubedexception import CsvToDataFrameLoadFailedException
from csvcubed.models.csvwtype import CSVWType
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.inspectdataframeresults import (
    CodelistHierarchyInfoResult,
    DatasetObservationsByMeasureUnitInfoResult,
    DatasetObservationsInfoResult,
)
from csvcubed.utils.pandas import read_csv
from csvcubed.utils.skos.codelist import build_concepts_hierarchy_tree

_logger = logging.getLogger(__name__)


def load_csv_to_dataframe(json_path: Path, csv_path: Path) -> pd.DataFrame:
    """
    Loads the csv in given path to a Panda Dataframe.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DataFrame` - Dataframe of the csv.
    """

    try:
        dataset_path = json_path.parent / csv_path
        _logger.debug(f"Dataset path: {dataset_path.absolute()}")

        dataset, data_errors = read_csv(dataset_path)
        for error in data_errors:
            _logger.warning(friendly_error_mapping(error))
        _logger.info("Successfully loaded csv into dataframe.")

        return dataset
    except Exception as ex:
        raise CsvToDataFrameLoadFailedException() from ex


def get_dataset_observations_info(
    dataset: pd.DataFrame, csvw_type: CSVWType, cube_shape: Optional[CubeShape]
) -> DatasetObservationsInfoResult:
    """
    Generates the `DatasetObservationsInfoResult` from the dataset.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetObservationsInfoResult`
    """

    return DatasetObservationsInfoResult(
        csvw_type,
        cube_shape,
        len(dataset.index),
        dataset.duplicated().sum(),
        dataset.head(n=10),
        dataset.tail(n=10),
    )


def get_dataset_val_counts_info(
    dataset: pd.DataFrame, measure_col: str, unit_col: str
) -> DatasetObservationsByMeasureUnitInfoResult:
    """
    Generates the `DatasetObservationsByMeasureUnitInfoResult` from the dataset.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetObservationsByMeasureUnitInfoResult`
    """
    _logger.debug(f"Dataset measure column name: {measure_col}")
    _logger.debug(f"Dataset unit column name: {unit_col}")

    by_measure_and_unit_grouped = dataset.groupby([measure_col, unit_col])

    return DatasetObservationsByMeasureUnitInfoResult(
        by_measure_and_unit_val_counts_df=pd.DataFrame(
            by_measure_and_unit_grouped.size().reset_index()
        ).rename(columns={measure_col: "Measure", unit_col: "Unit", 0: "Count"})
    )


def get_concepts_hierarchy_info(
    dataset: pd.DataFrame, parent_col, label_col, unique_identifier
) -> CodelistHierarchyInfoResult:
    """
    Generates the `CodelistHierarchyInfoResult` from the codelist.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `CodelistHierarchyInfoResult`
    """
    concepts_tree = build_concepts_hierarchy_tree(
        dataset, parent_col, label_col, unique_identifier
    )

    return CodelistHierarchyInfoResult(tree=concepts_tree)
