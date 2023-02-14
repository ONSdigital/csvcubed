"""
CSV Dataset
-----------

Utilities for CSV Datasets
"""

import logging
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import uuid1

import pandas as pd
import rdflib


from csvcubed.utils.sparql_handler.sparqlmanager import select_single_unit_from_dsd
from csvcubed.models.sparqlresults import QubeComponentResult
from csvcubed.models.inspectdataframeresults import DatasetSingleMeasureResult
from csvcubed.models.csvcubedexception import InvalidNumberOfRecordsException
from csvcubed.utils.qb.components import (
    ComponentField,
    ComponentPropertyType,
    ComponentPropertyAttributeURI,
    get_component_property_as_relative_path,
)

_logger = logging.getLogger(__name__)


def _filter_components_from_dsd(
    components: List[QubeComponentResult],
    field: ComponentField,
    filter: str,
) -> List[QubeComponentResult]:
    """
    Filters the components for the given filter.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `List[QubeComponentResult]` - filtered results.
    """

    return [
        component
        for component in components
        if component.as_dict()[field.value] == filter
    ]


def get_measure_col_name_from_dsd(
    components: List[QubeComponentResult],
) -> Optional[str]:
    """
    Identifies the name of measure column.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `Optional[str]`
    """
    filtered_components = _filter_components_from_dsd(
        components,
        ComponentField.Property,
        ComponentPropertyAttributeURI.MeasureType.value,
    )

    if len(filtered_components) == 0 or filtered_components[0].csv_col_title == "":
        _logger.warn(
            "Could not find measure column name from the DSD, hence returning None"
        )
        return None
    else:
        return filtered_components[0].csv_col_title


def get_unit_col_name_from_dsd(
    components: List[QubeComponentResult],
) -> Optional[str]:
    """
    Identifies the name of unit column.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `Optional[str]`
    """
    filtered_components = _filter_components_from_dsd(
        components,
        ComponentField.Property,
        ComponentPropertyAttributeURI.UnitMeasure.value,
    )

    if len(filtered_components) == 0 or filtered_components[0].csv_col_title == "":
        _logger.warn(
            "Could not find unit column name from the DSD, hence returning None"
        )
        return None
    else:
        return filtered_components[0].csv_col_title


def get_single_measure_from_dsd(
    components: List[QubeComponentResult], json_path: Path
) -> DatasetSingleMeasureResult:
    """
    Identifies the measure uri and label for single-measure dataset.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetSingleMeasureResult`
    """
    filtered_components = _filter_components_from_dsd(
        components, ComponentField.PropertyType, ComponentPropertyType.Measure.value
    )

    if len(filtered_components) != 1:
        raise InvalidNumberOfRecordsException(
            record_description="dsd components",
            excepted_num_of_records=1,
            num_of_records=len(filtered_components),
        )

    return DatasetSingleMeasureResult(
        measure_uri=get_component_property_as_relative_path(
            json_path, filtered_components[0].property
        ),
        measure_label=filtered_components[0].property_label,
    )

def transform_dataset_to_canonical_shape(
    dataset: pd.DataFrame,
    qube_components: List[QubeComponentResult],
    dataset_uri: str,
    csvw_metadata_rdf_graph: rdflib.ConjunctiveGraph,
    csvw_metadata_json_path: Path,
) -> Tuple[pd.DataFrame, str, str]:
    """
    Transforms the given dataset into canonical shape if it is not in the canonical shape already.

    Member of :class:`./csvdataset`.

    :return: `Tuple[pd.DataFrame, str, str]` - canonical dataframe, measure column name, unit column name.
    """
    canonical_shape_dataset = dataset.copy()

    measure_col: Optional[str] = get_measure_col_name_from_dsd(qube_components)
    unit_col: Optional[str] = get_unit_col_name_from_dsd(qube_components)

    if unit_col is None:
        unit_col = f"Unit_{str(uuid1())}"
        result = select_single_unit_from_dsd(
            csvw_metadata_rdf_graph,
            dataset_uri,
            csvw_metadata_json_path,
        )
        canonical_shape_dataset[unit_col] = (
            result.unit_label if result.unit_label is not None else result.unit_uri
        )

    if measure_col is None:
        measure_col = f"Measure_{str(uuid1())}"
        result = get_single_measure_from_dsd(qube_components, csvw_metadata_json_path)
        canonical_shape_dataset[measure_col] = (
            result.measure_label
            if result.measure_label is not None
            else result.measure_uri
        )
    return (canonical_shape_dataset, measure_col, unit_col)
