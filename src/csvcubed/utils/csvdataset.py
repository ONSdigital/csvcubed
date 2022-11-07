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
import rdflib
from csvcubed.utils.qb.components import ComponentField, ComponentPropertyType


from csvcubed.utils.sparql_handler.sparqlmanager import CSVWShape, select_single_unit_from_dsd
from csvcubed.models.sparqlresults import QubeComponentResult
from csvcubed.cli.inspect.inspectdatasetmanager import (
    filter_components_from_dsd,
    get_standard_shape_measure_col_name_from_dsd,
    get_single_measure_from_dsd,
    get_standard_shape_unit_col_name_from_dsd,
)


def transform_dataset_to_canonical_shape(
    csvw_shape: CSVWShape,
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

    unit_col: Optional[str] = get_standard_shape_unit_col_name_from_dsd(qube_components)

    if csvw_shape == CSVWShape.Standard:
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
        measure_col: Optional[str] = get_standard_shape_measure_col_name_from_dsd(qube_components)
    else:
        # In pivoted shape
        
        # STEP 1: Find the observation value columns by filtering components array by property type Measure. Keep a record of the measure uri also.
        measure_obs_val_components = filter_components_from_dsd(qube_components, ComponentField.PropertyType, ComponentPropertyType.Measure.value)


        # We need to melt the dataset if the shape is pivoted. To melt the dataset:
            # STEP 1: Find the observation value columns by filtering components array by property type Measure. Keep a record of the measure uri also.
            # STEP 2: Use the measure uri to get the measure label.
            # STEP 3: The values in the measure column in the melted dataset will be the measure label if one exists. Otherwise, use the measure uri.
            # STEP 4: Once we know the measure column values, melt the dataset using pandas melt. First try melting the below dataset, using pandas melt in the terminal.
            # Input pivoted dataset
                # Some Dimension, Obs Val 1, Obs Val 2
                # Birmingham, 22.5, 46
                # Manchester, 26.7, 44
                
            # Expected melted dataset
                # Some Dimension, Value, Measure, Unit
                # Birmingham, 22.5, Measure 1, Unit 1
                # Manchester, 26.7, Measure 1, Unit 1
                # Birmingham, 46, Measure 2, Unit 2
                # Manchester, 44, Measure 2, Unit 2
                
        measure_col = f"Measure_{str(uuid1())}"
        result = get_single_measure_from_dsd(qube_components, csvw_metadata_json_path)
        canonical_shape_dataset[measure_col] = (
            result.measure_label
            if result.measure_label is not None
            else result.measure_uri
        )

        # UNIT - TODO REDO STRUCTURE BELOW
        # Step 5: If the unit col title is none, get the unit from obs val column. 
        # Step 6: Otherwise, write a sparql that will first find the csvw virtual col definition for the unit given the property url http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure. Then use the aboutUrl of that def to find the Obs Val col that unit is associated with. Then use the valueUrl to find the unit uri from the obs val col.
        # Step 7: Use the unit uri to get the label of the unit. The unit label can none.

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
    
    
    return (canonical_shape_dataset, measure_col, unit_col)
