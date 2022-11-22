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
from csvcubed.models.sparqlresults import ObservationValueColumnTitleAboutUrlResult, QubeComponentResult, UnitColumnAboutValueUrlResult
from csvcubed.cli.inspect.inspectdatasetmanager import (
    filter_components_from_dsd,
    get_standard_shape_measure_col_name_from_dsd,
    get_single_measure_from_dsd,
    get_standard_shape_unit_col_name_from_dsd,
)

def _create_unit_col_in_melted_data_set(melted_df: pd.DataFrame, unit_col_about_urls_value_urls: List[UnitColumnAboutValueUrlResult], observation_value_col_titles_about_urls: List[ObservationValueColumnTitleAboutUrlResult]):
    """
    TODO: Add Description
    """
    melted_df["Unit"] = ""
    for idx, row in melted_df.iterrows():
        obs_val_col_title = row["Observation Value"]

        # Step 1: Use the observation value col title to get the unit col value url.
            # Step 1.1: First use the obs col title from for loop to get the about url from query 2 result. [DONE]
        
        filtered_observation_value_col_titles_about_urls = [observation_value_col_title_about_url for observation_value_col_title_about_url in observation_value_col_titles_about_urls if observation_value_col_title_about_url.observation_value_col_title == obs_val_col_title]

        if(len(filtered_observation_value_col_titles_about_urls) != 1):
            #TODO: Add relevant exception with inspect exceptions
            raise Exception("No matching result")

        observation_value_col_title_about_url = filtered_observation_value_col_titles_about_urls[0]
        about_url = observation_value_col_title_about_url.observation_value_col_about_url

            # Step 1.2: Then use the about url to get the unit col's value url from query 1 result. [DONE]

        filtered_unit_col_about_urls_value_urls = [unit_col_about_url_value_url for unit_col_about_url_value_url in unit_col_about_urls_value_urls if unit_col_about_url_value_url.about_url == about_url]
        
        if(len(filtered_unit_col_about_urls_value_urls) != 1):
            #TODO: Add relevant exception with inspect exceptions
            raise Exception("No matching result")

        unit_col_about_url_value_url = filtered_unit_col_about_urls_value_urls[0]
        unit_col_value_url = unit_col_about_url_value_url.value_url

        # Step 2: Use the uri template lib to tell me what the variables defined inside the unit value url are. These variables are col names.
            # If there are no varibales in unit value url, then set the unit column to be the unit value url.
            # Otherwise, for each variable named in the template uri, look up the csv column titles for each of them - query 3.  The variable names are the column names.
                # Get the values for col titles in this row, and provide a map to url template lib with a map of variable name and value to substitute. We are building the true url in here (only for this case.)

    # UNIT
    # Sparql query 1:
    # Filter on cols which are unit cols whether they are virtul or not. Pull out about url and value url both for the unit col.
        # About Url, Unit Value Url

    # # Sparql query 2:
    # Observed Value URL, Observed Val Col Title

    # # Sparql query 3: Returns a table of col names and titles.
    # Column Names, Column Title, 
    # units_column_name, Units Column Title, 

    
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
    cube_shape: CubeShape,
    dataset: pd.DataFrame,
    qube_components: List[QubeComponentResult],
    dataset_uri: str,
    unit_col_about_urls_value_urls: Optional[List[UnitColumnAboutValueUrlResult]],
    observation_value_col_titles_about_urls: Optional[List[ObservationValueColumnTitleAboutUrlResult]],
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

    if cube_shape == CubeShape.Standard:
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
        
        _create_unit_col_in_melted_data_set(melted_df, unit_col_about_urls_value_urls, observation_value_col_titles_about_urls)
        canonical_shape_dataset = melted_df

    return (canonical_shape_dataset, measure_col, unit_col)
