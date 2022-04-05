"""
CSV Dataset
-----------

Utilities for CSV Datasets
"""

from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import uuid1
import pandas as pd

from rdflib import Graph

from csvcubed.cli.inspect.inspectsparqlmanager import select_single_unit_from_dsd
from csvcubed.models.inspectsparqlresults import QubeComponentResult
from csvcubed.cli.inspect.inspectdatasetmanager import (
    get_measure_col_name_from_dsd,
    get_single_measure_from_dsd,
    get_unit_col_name_from_dsd,
)


def transform_dataset_to_canonical_shape(
    dataset: pd.DataFrame,
    qube_components: List[QubeComponentResult],
    dataset_uri: str,
    csvw_metadata_rdf_graph: Graph,
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
