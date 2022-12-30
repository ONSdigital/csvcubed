"""
CSV Dataset
-----------

Utilities for CSV Datasets
"""

from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from uuid import uuid1

import pandas as pd
import rdflib
import uritemplate
from uritemplate.orderedset import OrderedSet

from csvcubed.cli.inspect.inspectdatasetmanager import (
    filter_components_from_dsd,
    get_single_measure_from_dsd,
    get_standard_shape_measure_col_name_from_dsd,
    get_standard_shape_unit_col_name_from_dsd,
)
from csvcubed.models.csvcubedexception import (
    InvalidNumOfDSDComponentsForObsValColTitleException,
    InvalidNumOfUnitColsForObsValColTitleException,
    InvalidNumOfValUrlsForAboutUrlException,
)
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import (
    ColumnDefinition,
    ObservationValueColumnTitleAboutUrlResult,
    UnitColumnAboutValueUrlResult,
)
from csvcubed.models.sparqlresults import QubeComponentResult
from csvcubed.utils.iterables import first
from csvcubed.utils.qb.components import ComponentField, ComponentPropertyType
from csvcubed.utils.sparql_handler.data_cube_state import DataCubeState
from csvcubed.utils.sparql_handler.sparqlquerymanager import select_single_unit_from_dsd


def _materialise_unit_uri_for_row(
    unit_val_url_variable_names: OrderedSet,
    column_definitions: List[ColumnDefinition],
    unit_col_value_url: str,
    row: pd.Series,
):
    """
    Generates the unit column value url from the template.
    """
    col_name_value_map: Dict[str, Any] = {}
    for unit_val_url_variable_name in unit_val_url_variable_names:
        unit_column_definition = first(
            column_definitions, lambda u: u.name == unit_val_url_variable_name
        )

        if unit_column_definition:
            col_name_value_map[unit_val_url_variable_name] = row[
                unit_column_definition.title
            ]

    return uritemplate.expand(unit_col_value_url, col_name_value_map)


def _create_unit_col_in_melted_data_set_for_pivoted_shape(
    col_name: str,
    melted_df: pd.DataFrame,
    unit_col_about_urls_value_urls: List[UnitColumnAboutValueUrlResult],
    obs_val_col_titles_about_urls: List[ObservationValueColumnTitleAboutUrlResult],
    col_names_col_titles: List[ColumnDefinition],
):
    """
    Adds the unit column to the melted data set for the pivoted shape data set input.
    """
    # Creating a new column in pandas dataframe with empty values.
    melted_df[col_name] = ""

    for idx, row in melted_df.iterrows():
        observation_uri = _get_observation_uri_for_melted_df_row(
            obs_val_col_titles_about_urls, row
        )

        # Use the unit col's about url to get the unit col's value url.
        # N.B., for an old-style single measure pivoted shape, the following filter still works as the
        # about url and observation uri are both None (i.e. equal).
        unit_col_about_url_value_url = first(
            unit_col_about_urls_value_urls, lambda u: u.about_url == observation_uri
        )
        if unit_col_about_url_value_url is None:
            raise InvalidNumOfValUrlsForAboutUrlException(
                about_url=observation_uri or "None",
                num_of_value_urls=0,
            )
        unit_col_value_url = unit_col_about_url_value_url.value_url

        # Get the variable names in the unit col's value url.
        unit_val_url_variable_names = uritemplate.variables(unit_col_value_url)
        # If there are no variable names, the unit is the unit col's value url.
        if not any(unit_val_url_variable_names):
            melted_df.loc[idx, col_name] = unit_col_value_url
        else:
            # If there are variable names, identify the column titles for the variable names and generate
            # the unit value url, and set it as the unit.
            processed_unit_value_url = _materialise_unit_uri_for_row(
                unit_val_url_variable_names,
                col_names_col_titles,
                unit_col_value_url,
                row,
            )
            melted_df.loc[idx, col_name] = processed_unit_value_url


def _get_observation_uri_for_melted_df_row(
    obs_val_col_titles_about_urls: List[ObservationValueColumnTitleAboutUrlResult],
    row: pd.Series,
) -> Optional[str]:
    obs_val_col_title = str(row["Observation Value"])
    # Use the observation value col title to get the unit col's about url.
    obs_val_col_title_about_url = first(
        obs_val_col_titles_about_urls,
        lambda o: o.observation_value_col_title == obs_val_col_title,
    )
    if obs_val_col_title_about_url is None:
        raise InvalidNumOfUnitColsForObsValColTitleException(
            obs_val_col_title=obs_val_col_title,
            num_of_unit_cols=0,
        )
    return obs_val_col_title_about_url.observation_value_col_about_url


def _create_measure_col_in_melted_data_set_for_pivoted_shape(
    col_name: str,
    melted_df: pd.DataFrame,
    measure_components: List[QubeComponentResult],
):
    """
    Associates the relevant measure information with each observation value
    """
    # Creating a new column in pandas dataframe with empty values.
    melted_df[col_name] = ""

    for idx, row in melted_df.iterrows():
        obs_val_col_title = str(row["Observation Value"])
        filtered_measure_components = [
            comp
            for comp in measure_components
            if obs_val_col_title in {col.title for col in comp.used_in_columns}
        ]

        if len(filtered_measure_components) != 1:
            raise InvalidNumOfDSDComponentsForObsValColTitleException(
                obs_val_col_title=obs_val_col_title,
                num_of_components=len(filtered_measure_components),
            )

        measure_component = first(filtered_measure_components)
        # Using the measure label if it exists as it is more user-friendly. Otherwise, we use the measure uri.
        melted_df.loc[idx, col_name] = (
            measure_component.property_label
            if measure_component.property_label
            else measure_component.property
        )


def _melt_data_set(
    data_set: pd.DataFrame, measure_components: List[QubeComponentResult]
) -> pd.DataFrame:
    """
    Melts a pivoted shape data set in preparation for extracting the measure and unit information as separate columns
    """
    # Finding the value cols and id cols for melting the data set.
    value_cols = [
        c.title
        for measure_component in measure_components
        for c in measure_component.used_in_columns
    ]
    id_cols = list(set(data_set.columns) - set(value_cols))

    # Melting the data set using pandas melt function.
    return pd.melt(
        data_set,
        id_vars=id_cols,
        value_vars=value_cols,
        value_name="Value",
        var_name="Observation Value",
    )


def transform_dataset_to_canonical_shape(
    data_cube_state: DataCubeState,
    dataset: pd.DataFrame,
    qube_components: List[QubeComponentResult],
    csv_url: str,
    csvw_metadata_rdf_graph: rdflib.ConjunctiveGraph,
    csvw_metadata_json_path: Path,
) -> Tuple[pd.DataFrame, str, str]:
    """
    Transforms the given dataset into canonical shape if it is not in the canonical shape already.

    Member of :class:`./csvdataset`.

    :return: `Tuple[pd.DataFrame, str, str]` - canonical dataframe, measure column name, unit column name.
    """
    canonical_shape_dataset = dataset.copy()
    unit_col: str
    measure_col: str

    cube_identifiers = data_cube_state.get_cube_identifiers_for_csv(csv_url)
    cube_shape = data_cube_state.get_shape_for_csv(csv_url)

    if cube_shape == CubeShape.Standard:
        unit_col_retrived = get_standard_shape_unit_col_name_from_dsd(qube_components)
        if unit_col_retrived is None:
            unit_col = f"Unit_{str(uuid1())}"
            result = select_single_unit_from_dsd(
                csvw_metadata_rdf_graph,
                cube_identifiers.dsd_uri,
                csvw_metadata_json_path,
            )
            canonical_shape_dataset[unit_col] = (
                result.unit_label if result.unit_label is not None else result.unit_uri
            )
        else:
            unit_col = unit_col_retrived

        measure_col_retrived = get_standard_shape_measure_col_name_from_dsd(
            qube_components
        )
        if measure_col_retrived is None:
            measure_col = f"Measure_{str(uuid1())}"
            result = get_single_measure_from_dsd(
                qube_components, csvw_metadata_json_path
            )
            canonical_shape_dataset[measure_col] = (
                result.measure_label
                if result.measure_label is not None
                else result.measure_uri
            )
        else:
            measure_col = measure_col_retrived
    else:
        # In pivoted shape
        if csv_url is None:
            raise ValueError("csv_url cannot be None.")

        unit_col_about_urls_value_urls = (
            data_cube_state.get_unit_col_about_value_urls_for_csv(csv_url)
        )
        obs_val_col_titles_about_urls = (
            data_cube_state.get_obs_val_col_titles_about_urls_for_csv(csv_url)
        )
        col_names_col_titles = data_cube_state.get_column_definitions_for_csv(csv_url)

        measure_components = filter_components_from_dsd(
            qube_components,
            ComponentField.PropertyType,
            ComponentPropertyType.Measure.value,
        )
        melted_df = _melt_data_set(canonical_shape_dataset, measure_components)

        measure_col = f"Measure_{str(uuid1())}"
        unit_col = f"Unit_{str(uuid1())}"
        _create_measure_col_in_melted_data_set_for_pivoted_shape(
            measure_col, melted_df, measure_components
        )
        _create_unit_col_in_melted_data_set_for_pivoted_shape(
            unit_col,
            melted_df,
            unit_col_about_urls_value_urls,
            obs_val_col_titles_about_urls,
            col_names_col_titles,
        )

        canonical_shape_dataset = melted_df.drop("Observation Value", axis=1)

    return (canonical_shape_dataset, measure_col, unit_col)
