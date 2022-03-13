"""
Inspect Dataset Manager
-----------------------

Collection of functions handling csv-related operations used in the inspect cli.
"""


import logging
from enum import Enum
from pathlib import Path
from csvcubed.cli.inspect.inspectsparqlmanager import select_csvw_dsd_qube_components
from csvcubed.models.inspectsparqlresults import QubeComponentsResult
from csvcubed.utils.qb.components import (
    COMPONENT_PROPERTY_ATTRIBUTE_UNITMEASURE,
    ComponentPropertyType,
    ComponentPropertyTypeURI,
)
import pandas as pd
from pandas import DataFrame

from csvcubed.models.inspectdataframeresults import (
    DatasetObservationsByMeasureUnitInfoResult,
    DatasetObservationsInfoResult,
)
from rdflib import Graph, URIRef

_logger = logging.getLogger(__name__)


class DatasetMeasureType(Enum):
    """
    The type of dataset measure.
    """

    SINGLE_MEASURE = 0

    MULTI_MEASURE = 1


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


def get_single_measure_dataset_val_counts_info(
    dataset: DataFrame,
) -> DatasetObservationsByMeasureUnitInfoResult:
    """
    Generates the `DatasetObservationsByMeasureUnitInfoResult` from the single-measure dataset.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetObservationsByMeasureUnitInfoResult`
    """

    # TODO: Implement for single-measure dataset.
    return DatasetObservationsByMeasureUnitInfoResult(
        by_measure_and_unit_val_counts_df=DataFrame()
    )


def get_multi_measure_dataset_val_counts_info(
    dataset: DataFrame, unit_label=None
) -> DatasetObservationsByMeasureUnitInfoResult:
    """
    Generates the `DatasetObservationsByMeasureUnitInfoResult` from the multi-measure dataset.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetObservationsByMeasureUnitInfoResult`
    """
    if unit_label is not None:
        by_measure_and_unit_grouped_df = dataset.groupby(["Measure Type", "Unit"])
    else:
        by_measure_and_unit_grouped_df = dataset.groupby("Measure Type")
        # TODO Add new col to df with Unit.

    return DatasetObservationsByMeasureUnitInfoResult(
        by_measure_and_unit_val_counts_df=DataFrame(
            by_measure_and_unit_grouped_df.size().reset_index(name="count")
        ),
    )


def get_dataset_measure_type(
    graph: Graph, dsd_uri: URIRef, json_path: Path
) -> DatasetMeasureType:
    """
    Detects whether the dataset is single-measure or multi-measure.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetMeasureType`
    """
    result_qube_components: QubeComponentsResult = select_csvw_dsd_qube_components(
        graph, dsd_uri, json_path
    )
    filtered_components = [
        component
        for component in result_qube_components.qube_components
        if component.property_type == ComponentPropertyType.Measure.value
    ]
    return (
        DatasetMeasureType.MULTI_MEASURE
        if len(filtered_components) > 1
        else DatasetMeasureType.SINGLE_MEASURE
    )


def get_dataset_unit_type(graph: Graph, dsd_uri, json_path: Path) -> DatasetUnitType:
    """
    Detects whether the dataset is single-unit or multi-unit.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetUnitType`
    """
    result_qube_components: QubeComponentsResult = select_csvw_dsd_qube_components(
        graph, dsd_uri, json_path
    )
    filtered_components = [
        component
        for component in result_qube_components.qube_components
        if component.property == COMPONENT_PROPERTY_ATTRIBUTE_UNITMEASURE
    ]
    return (
        DatasetUnitType.MULTI_UNIT
        if len(filtered_components) > 0
        else DatasetUnitType.SINGLE_UNIT
    )
