"""
Inspect Dataset Manager
-----------------------

Collection of functions handling csv-related operations used in the inspect cli.
"""


import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd

from csvcubed.cli.error_mapping import friendly_error_mapping
from csvcubed.models.csvcubedexception import (
    CsvToDataFrameLoadFailedException,
    InvalidNumberOfRecordsException,
)
from csvcubed.models.csvwtype import CSVWType
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.inspectdataframeresults import (
    CodelistHierarchyInfoResult,
    DatasetObservationsByMeasureUnitInfoResult,
    DatasetObservationsInfoResult,
    DatasetSingleMeasureResult,
)
from csvcubed.models.sparqlresults import QubeComponentResult
from csvcubed.utils.iterables import first
from csvcubed.utils.pandas import read_csv
from csvcubed.utils.qb.components import (
    ComponentField,
    ComponentPropertyAttributeURI,
    ComponentPropertyType,
    get_component_property_as_relative_path,
)
from csvcubed.utils.skos.codelist import build_concepts_hierarchy_tree

_logger = logging.getLogger(__name__)


def filter_components_from_dsd(
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


def get_standard_shape_measure_col_name_from_dsd(
    components: List[QubeComponentResult],
) -> Optional[str]:
    """
    Identifies the name of the measure column in a standard shape data set.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `Optional[str]`
    """
    measure_components = filter_components_from_dsd(
        components,
        ComponentField.Property,
        ComponentPropertyAttributeURI.MeasureType.value,
    )

    first_measure_component = first(measure_components)

    if (
        first_measure_component is not None
        and len(first_measure_component.real_columns_used_in) == 1
    ):
        csv_measure_column = first_measure_component.real_columns_used_in[0]
        return csv_measure_column.title
    else:
        _logger.warning(
            "Could not find measure column name from the DSD, hence returning None"
        )
        return None


def get_standard_shape_unit_col_name_from_dsd(
    components: List[QubeComponentResult],
) -> Optional[str]:
    """
    Identifies the name of unit column in a standard shaped data set.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `Optional[str]`
    """
    unit_components = filter_components_from_dsd(
        components,
        ComponentField.Property,
        ComponentPropertyAttributeURI.UnitMeasure.value,
    )

    first_unit_component = first(unit_components)

    if (
        first_unit_component is not None
        and len(first_unit_component.real_columns_used_in) == 1
    ):
        csv_units_column = first_unit_component.real_columns_used_in[0]
        return csv_units_column.title
    else:
        _logger.warning(
            "Could not find unit column name from the DSD, hence returning None"
        )
        return None


def get_single_measure_from_dsd(
    components: List[QubeComponentResult], json_path: Path
) -> DatasetSingleMeasureResult:
    """
    Identifies the measure uri and label for single-measure dataset.

    Member of :file:`./inspectdatasetmanager.py`

    :return: `DatasetSingleMeasureResult`
    """
    filtered_components = filter_components_from_dsd(
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
        )
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
