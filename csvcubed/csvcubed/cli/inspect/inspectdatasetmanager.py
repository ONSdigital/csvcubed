"""
Inspect Dataset Manager
-----------------------

Collection of functions handling csv-related operations used in the inspect cli.
"""


import logging
from enum import Enum, auto
from pathlib import Path
from typing import List
import pandas as pd
from pandas import DataFrame

from rdflib import Graph, URIRef

from csvcubed.cli.inspect.inspectsparqlmanager import select_csvw_dsd_qube_components
from csvcubed.models.inspectsparqlresults import (
    QubeComponentResult,
    QubeComponentsResult,
)
from csvcubed.utils.qb.components import (
    ComponentField,
    ComponentPropertyAttributeURI,
    ComponentPropertyType,
)
from csvcubed.models.inspectdataframeresults import (
    DatasetObservationsByMeasureUnitInfoResult,
    DatasetObservationsInfoResult,
)
from csvcubed.utils.csvdataset import CanonicalShapeRequiredCols

_logger = logging.getLogger(__name__)


class DatasetMeasureType(Enum):
    """
    The type of dataset measure.
    """

    SINGLE_MEASURE = auto()

    MULTI_MEASURE = auto()


class DatasetUnitType(Enum):
    """
    The type of dataset unit.
    """

    SINGLE_UNIT = auto()

    MULTI_UNIT = auto()


def _filter_components_from_dsd(
    graph: Graph, dsd_uri: URIRef, json_path: str, field: ComponentField, filter: str
) -> List[QubeComponentResult]:
    """
    Filters the components for the given filter.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `List[QubeComponentResult]` - filtered results.
    """
    result_qube_components: QubeComponentsResult = select_csvw_dsd_qube_components(
        graph, dsd_uri, json_path
    )

    return [
        component
        for component in result_qube_components.qube_components
        if component.as_dict()[field.value] == filter
    ]


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


def get_dataset_measure_type(
    graph: Graph, dsd_uri: URIRef, json_path: Path
) -> DatasetMeasureType:
    """
    Detects whether the dataset is single-measure or multi-measure.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetMeasureType`
    """
    filtered_components = _filter_components_from_dsd(
        graph,
        dsd_uri,
        json_path,
        ComponentField.PropertyType,
        ComponentPropertyType.Measure.value,
    )
    measure_type = (
        DatasetMeasureType.MULTI_MEASURE
        if len(filtered_components) > 1
        else DatasetMeasureType.SINGLE_MEASURE
    )
    _logger.debug(f"Dataset measure type: {measure_type}")

    return measure_type


def get_dataset_unit_type(dataset: DataFrame) -> DatasetUnitType:
    """
    Detects whether the dataset is single-unit or multi-unit.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetUnitType`
    """
    unit_type = (
        DatasetUnitType.MULTI_UNIT
        if len(dataset[CanonicalShapeRequiredCols.Unit.value].unique()) > 1
        else DatasetUnitType.SINGLE_UNIT
    )
    _logger.debug(f"Dataset unit type: {unit_type}")

    return unit_type


def get_measure_col_from_dsd(graph: Graph, dsd_uri, json_path: Path) -> str:
    """
    Identifies the name of measure column.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `str`
    """
    filtered_components = _filter_components_from_dsd(
        graph,
        dsd_uri,
        json_path,
        ComponentField.Property,
        ComponentPropertyAttributeURI.MeasureType.value,
    )

    if len(filtered_components) != 1:
        raise Exception(f"Expected 1 record, but found {len(filtered_components)}")

    return filtered_components[0].csv_col_title


def get_unit_col_from_dsd(graph: Graph, dsd_uri, json_path: Path) -> str:
    """
    Identifies the name of unit column.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `str`
    """
    filtered_components = _filter_components_from_dsd(
        graph,
        dsd_uri,
        json_path,
        ComponentField.Property,
        ComponentPropertyAttributeURI.UnitMeasure.value,
    )

    if len(filtered_components) != 1:
        raise Exception(f"Expected 1 record, but found {len(filtered_components)}")

    return filtered_components[0].csv_col_title


def get_single_measure_label_from_dsd(graph: Graph, dsd_uri, json_path: Path) -> str:
    """
    Identifies the measure label for single-measure dataset.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `str`
    """
    filtered_components = _filter_components_from_dsd(
        graph,
        dsd_uri,
        json_path,
        ComponentField.Property,
        ComponentPropertyAttributeURI.MeasureType.value,
    )

    if len(filtered_components) != 1:
        raise Exception(f"Expected 1 record, but found {len(filtered_components)}")

    return filtered_components[0].property_label


def get_single_unit_label_from_dsd(graph: Graph, dsd_uri, json_path: Path) -> str:
    """
    Identifies the unit label for single-measure dataset.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `str`
    """
    filtered_components = _filter_components_from_dsd(
        graph,
        dsd_uri,
        json_path,
        ComponentField.Property,
        ComponentPropertyAttributeURI.UnitMeasure.value,
    )

    if len(filtered_components) != 1:
        raise Exception(f"Expected 1 record, but found {len(filtered_components)}")

    return filtered_components[0].property_label


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
    measure_col: str,
    unit_col: str,
    measure_label: str,
    unit_label: str,
) -> DatasetObservationsByMeasureUnitInfoResult:
    """
    Generates the `DatasetObservationsByMeasureUnitInfoResult` from the single-measure dataset.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetObservationsByMeasureUnitInfoResult`
    """
    _logger.debug(f"Dataset measure column: {measure_col}")
    _logger.debug(f"Dataset unit column: {unit_col}")

    if measure_col == "" or unit_col == "":
        raise Exception("Measure column name and/or Unit column name is invalid.")

    data = {
        measure_col: [measure_label],
        unit_col: [unit_label],
        "Count": dataset.shape[0],
    }

    return DatasetObservationsByMeasureUnitInfoResult(
        by_measure_and_unit_val_counts_df=DataFrame(data)
    )


def get_multi_measure_dataset_val_counts_info(
    dataset: DataFrame, measure_col: str, unit_col: str
) -> DatasetObservationsByMeasureUnitInfoResult:
    """
    Generates the `DatasetObservationsByMeasureUnitInfoResult` from the multi-measure dataset.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetObservationsByMeasureUnitInfoResult`
    """
    _logger.debug(f"Dataset measure column: {measure_col}")
    _logger.debug(f"Dataset unit column: {unit_col}")

    by_measure_and_unit_grouped = dataset.groupby([measure_col, unit_col])

    return DatasetObservationsByMeasureUnitInfoResult(
        by_measure_and_unit_val_counts_df=DataFrame(
            by_measure_and_unit_grouped.size().reset_index()
        )
    )
