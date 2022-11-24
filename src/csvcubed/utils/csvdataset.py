"""
CSV Dataset
-----------

Utilities for CSV Datasets
"""

import numpy as np
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from uuid import uuid1
import uritemplate

import pandas as pd
import rdflib
from csvcubed.utils.qb.components import ComponentField, ComponentPropertyAttributeURI, ComponentPropertyType


from csvcubed.utils.sparql_handler.sparqlmanager import CubeShape, select_single_unit_from_dsd
from csvcubed.models.sparqlresults import ColTitlesAndNamesResult, ObservationValueColumnTitleAboutUrlResult, QubeComponentResult, UnitColumnAboutValueUrlResult
from csvcubed.cli.inspect.inspectdatasetmanager import (
    filter_components_from_dsd,
    get_standard_shape_measure_col_name_from_dsd,
    get_single_measure_from_dsd,
    get_standard_shape_unit_col_name_from_dsd,
)

def _create_unit_col_in_melted_data_set(melted_df: pd.DataFrame, unit_col_about_urls_value_urls: List[UnitColumnAboutValueUrlResult], obs_val_col_titles_about_urls: List[ObservationValueColumnTitleAboutUrlResult], col_names_col_titles: List[ColTitlesAndNamesResult]):
    """
    TODO: Add Description
    """
    melted_df["Unit"] = ""
    for idx, row in melted_df.iterrows():
        obs_val_col_title = row["Observation Value"]

        # Use the observation value col title to get the unit col's about url.
        filtered_obs_val_col_titles_about_urls = [obs_val_col_title_about_url for obs_val_col_title_about_url in obs_val_col_titles_about_urls if obs_val_col_title_about_url.observation_value_col_title == obs_val_col_title]
        if(len(filtered_obs_val_col_titles_about_urls) != 1):
            #TODO: Add relevant exception with inspect exceptions
            raise Exception("No matching result")
        obs_val_col_title_about_url = filtered_obs_val_col_titles_about_urls[0]
        about_url = obs_val_col_title_about_url.observation_value_col_about_url

        # Use the uit col's about url to get the unit col's value url.
        filtered_unit_col_about_urls_value_urls = [unit_col_about_url_value_url for unit_col_about_url_value_url in unit_col_about_urls_value_urls if unit_col_about_url_value_url.about_url == about_url]
        if(len(filtered_unit_col_about_urls_value_urls) != 1):
            #TODO: Add relevant exception with inspect exceptions
            raise Exception("No matching result")
        unit_col_about_url_value_url = filtered_unit_col_about_urls_value_urls[0]
        unit_col_value_url = unit_col_about_url_value_url.value_url

        # Get the variable names in the unit col's value url.
        unit_val_url_variable_names = uritemplate.variables(unit_col_value_url)
        # If there are no variable names, the unit is the unit col's value url.
        if (len(unit_val_url_variable_names) == 0):
            melted_df.loc[idx, "Unit"] = unit_col_value_url
        else:
            # If there are variable names, identify the column titles for the variable names and generate the unit value url, and set it as the unit.
            col_name_value_map: Dict[str,str] = {}
            for unit_val_url_variable_name in unit_val_url_variable_names:
                filtered_col_names_titles = [col_name_col_title for col_name_col_title in col_names_col_titles if col_name_col_title.column_name == unit_val_url_variable_name]
                if(len(filtered_col_names_titles) != 1):
                    #TODO: Add relevant exception with inspect exceptions
                    raise Exception("No matching result")
                col_title = filtered_col_names_titles[0].column_title
                col_name_value_map[unit_val_url_variable_name] = row[col_title]
            
            processed_unit_value_url = uritemplate.expand(unit_col_value_url, col_name_value_map)
            melted_df.loc[idx, "Unit"] = processed_unit_value_url

def _create_measure_col_in_melted_data_set(melted_df: pd.DataFrame, measure_components: List[QubeComponentResult]):
    """
    Associates the relevant measure information with each observation value
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
    Melts a pivoted shape data set in preparation for extracting the measure and unit information as separate columns
    """
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
    obs_val_col_titles_about_urls: Optional[List[ObservationValueColumnTitleAboutUrlResult]],
    col_names_col_titles: Optional[List[ColTitlesAndNamesResult]],
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
        
        _create_unit_col_in_melted_data_set(melted_df, unit_col_about_urls_value_urls, obs_val_col_titles_about_urls, col_names_col_titles)
        
        canonical_shape_dataset = melted_df
        
    return (canonical_shape_dataset, measure_col, unit_col)
