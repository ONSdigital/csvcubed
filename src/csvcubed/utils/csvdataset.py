"""
CSV Dataset
-----------

Utilities for CSV Datasets
"""

import numpy as np
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import uuid1

import pandas as pd
import rdflib
from csvcubed.utils.qb.components import ComponentField, ComponentPropertyAttributeURI, ComponentPropertyType


from csvcubed.utils.sparql_handler.sparqlmanager import CubeShape, select_single_unit_from_dsd
from csvcubed.models.sparqlresults import QubeComponentResult
from csvcubed.cli.inspect.inspectdatasetmanager import (
    filter_components_from_dsd,
    get_standard_shape_measure_col_name_from_dsd,
    get_single_measure_from_dsd,
    get_standard_shape_unit_col_name_from_dsd,
)

def _create_unit_col_in_melted_data_set(melted_df: pd.DataFrame, unit_components: List[QubeComponentResult]):
    """
    TODO: Add Description
    """
    melted_df["Unit"] = ""

    # UNIT - TODO
    # Sparql query 1:
    # Obs Val Col, Unit column's valueUrl Template
    # Observed Val Column Title (Found via the about Url of the units col), http://example.com/units/the-unit (uri of the unit) <- virtual col case
    # Observed Val Column Title (Found via the about Url of the units col), http://example.com/units/{+units_column_name} <- real col case

    # # Sparql query 2:
    # Observed Value URL, Observed Val Col Title

    # # Sparql query 3:
    # Column Title, Column Names
    # Units Column Title, units_column_name

    
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


def _create_measure_col_in_melted_data_set(melted_df: pd.DataFrame, measure_components: List[QubeComponentResult]):
    """
    TODO: Add Description
    """
    # Adding the Measure column into the melted data set.
    melted_df["Measure"] = ""
    for idx, row in melted_df.iterrows():
        obs_val_col_title = row["Observation Value"]
        filtered_measure_components = filter_components_from_dsd(measure_components, ComponentField.CsvColumnTitle, obs_val_col_title)
        
        if len(filtered_measure_components) != 1:
            #TODO: Create new exception in inspect exceptions
            raise Exception("Expected one observation value component")
        
        measure_component = filtered_measure_components[0]
        # Using the measure label if it exists as it is more user-friendly. Otherwise, we use the measure uri.
        melted_df.loc[idx, "Measure"] = measure_component.property_label if measure_component.property_label else measure_component.property
       
def _melt_data_set(data_set: pd.DataFrame, measure_components: List[QubeComponentResult]) -> pd.DataFrame:
    """
    TODO: Add Description
    """
    # MEASURE - DONE
    #  We need to melt the dataset if the shape is pivoted. To melt the dataset:
        # STEP 1: Find the observation value columns by filtering components array by property type Measure. Keep a record of the measure uri also.
        # STEP 2: Use the measure uri to get the measure label.
        # STEP 3: The values in the measure column in the melted dataset will be the measure label if one exists. Otherwise, use the measure uri.
        # STEP 4: Once we know the measure column values, melt the dataset using pandas melt. First try melting the below dataset, using pandas melt in the terminal.
        
    # Finding the value cols and id cols for melting the data set.
    value_cols = [
                    measure_component.csv_col_title 
                    for measure_component in measure_components
                ]
    id_cols = list(set(data_set.columns) - set(value_cols))

    # Melting the data set using pandas melt function.
    return pd.melt(
        data_set, id_vars=id_cols, value_vars=value_cols, value_name="Value", var_name="Observation Value"
    )
    
def transform_dataset_to_canonical_shape(
    csvw_shape: CubeShape,
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

    unit_col: Optional[str] = None
    measure_col: Optional[str] = None

    if csvw_shape == CubeShape.Standard:
        unit_col = get_standard_shape_unit_col_name_from_dsd(qube_components)
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
        measure_col = get_standard_shape_measure_col_name_from_dsd(qube_components)
    else:
        # In pivoted shape
        measure_components = filter_components_from_dsd(qube_components, ComponentField.PropertyType, ComponentPropertyType.Measure.value)        
        melted_df = _melt_data_set(canonical_shape_dataset, measure_components)
        _create_measure_col_in_melted_data_set(melted_df, measure_components)

        unit_components = filter_components_from_dsd(qube_components, ComponentField.Property, ComponentPropertyAttributeURI.UnitMeasure)
        _create_unit_col_in_melted_data_set(melted_df, unit_components)
        canonical_shape_dataset = melted_df

    return (canonical_shape_dataset, measure_col, unit_col)
