"""
CSV Dataset
-----------

Utilities for CSV Datasets
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
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
    InvalidNumberOfRecordsException,
    InvalidNumOfDSDComponentsForObsValColTitleException,
    InvalidNumOfUnitColsForObsValColTitleException,
    InvalidNumOfValUrlsForAboutUrlException,
)
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import (
    ColTitlesAndNamesResult,
    ObservationValueColumnTitleAboutUrlResult,
    QubeComponentResult,
    UnitColumnAboutValueUrlResult,
)
from csvcubed.utils.iterables import first
from csvcubed.utils.qb.components import ComponentField, ComponentPropertyType
from csvcubed.utils.sparql_handler.data_cube_state import DataCubeState


def _materialise_unit_uri_for_row(
    unit_val_url_variable_names: OrderedSet,
    col_names_col_titles: List[ColTitlesAndNamesResult],
    unit_col_value_url: str,
    row: pd.Series,
):
    """
    Generates the unit column value url from the template.
    """
    col_name_value_map: Dict[str, Any] = {}
    for unit_val_url_variable_name in unit_val_url_variable_names:
        col_name_col_title = first(
            col_names_col_titles, lambda u: u.column_name == unit_val_url_variable_name
        )

        if col_name_col_title:
            col_name_value_map[unit_val_url_variable_name] = row[
                col_name_col_title.column_title
            ]

    return uritemplate.expand(unit_col_value_url, col_name_value_map)


def _create_unit_col_in_melted_data_set_for_pivoted_shape(
    col_name: str,
    melted_df: pd.DataFrame,
    unit_col_about_urls_value_urls: List[UnitColumnAboutValueUrlResult],
    obs_val_col_titles_about_urls: List[ObservationValueColumnTitleAboutUrlResult],
    col_names_col_titles: List[ColTitlesAndNamesResult],
    data_cube_state: DataCubeState,
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

        unit_uri = _get_unit_uri_for_maybe_template(
            unit_col_about_url_value_url.value_url, col_names_col_titles, row
        )
        maybe_unit = data_cube_state.get_unit_for_uri(unit_uri)
        if maybe_unit is None:
            melted_df.loc[idx, col_name] = unit_uri
        else:
            melted_df.loc[idx, col_name] = maybe_unit.unit_label


def _get_unit_uri_for_maybe_template(
    template_url: str,
    col_names_col_titles: List[ColTitlesAndNamesResult],
    row: pd.Series,
) -> str:
    # Get the variable names in the unit col's value url.
    unit_val_url_variable_names = uritemplate.variables(template_url)
    # If there are no variable names, the unit is the unit col's value url.
    if not any(unit_val_url_variable_names):
        return template_url
    else:
        # If there are variable names, identify the column titles for the variable names and generate the unit value url, and set it as the unit.
        return _materialise_unit_uri_for_row(
            unit_val_url_variable_names,
            col_names_col_titles,
            template_url,
            row,
        )


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
        filtered_measure_components = filter_components_from_dsd(
            measure_components, ComponentField.CsvColumnTitle, obs_val_col_title
        )

        if len(filtered_measure_components) != 1:
            raise InvalidNumOfDSDComponentsForObsValColTitleException(
                obs_val_col_title=obs_val_col_title,
                num_of_components=len(filtered_measure_components),
            )

        measure_component = filtered_measure_components[0]
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
        measure_component.csv_col_title for measure_component in measure_components
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


def cube_in_standard_shape(
    qube_components: List[QubeComponentResult],
    data_cube_state: DataCubeState,
    canonical_shape_dataset: pd.DataFrame,
    csvw_metadata_json_path: Path,
) -> Tuple[pd.DataFrame, str, str]:
    unit_col_retrived = get_standard_shape_unit_col_name_from_dsd(qube_components)
    if unit_col_retrived is None:
        unit_col = f"Unit_{str(uuid1())}"
        units = data_cube_state.get_units()
        if len(units) != 1:
            raise InvalidNumberOfRecordsException(
                record_description=f"result for the `get_units()` function call",
                excepted_num_of_records=1,
                num_of_records=len(units),
            )
        unit = units[0]
        canonical_shape_dataset[unit_col] = unit.unit_label
    else:
        unit_col = unit_col_retrived

    measure_col_retrived = get_standard_shape_measure_col_name_from_dsd(qube_components)
    if measure_col_retrived is None:
        measure_col = f"Measure_{str(uuid1())}"
        result = get_single_measure_from_dsd(qube_components, csvw_metadata_json_path)
        canonical_shape_dataset[measure_col] = (
            result.measure_label
            if result.measure_label is not None
            else result.measure_uri
        )
    else:
        measure_col = measure_col_retrived

    return (canonical_shape_dataset, measure_col, unit_col)


def cube_in_pivoted_shape(
    csv_url: str,
    data_cube_state: DataCubeState,
    qube_components: List[QubeComponentResult],
    canonical_shape_dataset: pd.DataFrame,
) -> Tuple[pd.DataFrame, str, str]:
    if csv_url is None:
        raise ValueError("csv_url cannot be None.")

    unit_col_about_urls_value_urls = (
        data_cube_state.get_unit_col_about_value_urls_for_csv(csv_url)
    )
    obs_val_col_titles_about_urls = (
        data_cube_state.get_obs_val_col_titles_about_urls_for_csv(csv_url)
    )
    col_names_col_titles = data_cube_state.get_col_name_col_title_for_csv(csv_url)

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
        data_cube_state,
    )

    canonical_shape_dataset = melted_df.drop("Observation Value", axis=1)

    return (canonical_shape_dataset, measure_col, unit_col)


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
        return cube_in_standard_shape(
            qube_components,
            data_cube_state,
            canonical_shape_dataset,
            csvw_metadata_json_path,
        )
        # unit_col_retrived = get_standard_shape_unit_col_name_from_dsd(qube_components)
        # if unit_col_retrived is None:
        #    unit_col = f"Unit_{str(uuid1())}"
        #    units = data_cube_state.get_units()
        #    if len(units) != 1:
        #        raise InvalidNumberOfRecordsException(
        #            record_description=f"result for the `get_units()` function call",
        #            excepted_num_of_records=1,
        #            num_of_records=len(units),
        #        )
        #    unit = units[0]
        #    canonical_shape_dataset[unit_col] = unit.unit_label
        # else:
        #    unit_col = unit_col_retrived

        # measure_col_retrived = get_standard_shape_measure_col_name_from_dsd(
        #    qube_components
        # )
        # if measure_col_retrived is None:
        #    measure_col = f"Measure_{str(uuid1())}"
        #    result = get_single_measure_from_dsd(
        #        qube_components, csvw_metadata_json_path
        #    )
        #    canonical_shape_dataset[measure_col] = (
        #        result.measure_label
        #        if result.measure_label is not None
        #        else result.measure_uri
        #    )
        # else:
        #    measure_col = measure_col_retrived
    else:
        # In pivoted shape
        return cube_in_pivoted_shape(
            csv_url, data_cube_state, qube_components, canonical_shape_dataset
        )
        # if csv_url is None:
        #    raise ValueError("csv_url cannot be None.")


"""         unit_col_about_urls_value_urls = (
            data_cube_state.get_unit_col_about_value_urls_for_csv(csv_url)
        )
        obs_val_col_titles_about_urls = (
            data_cube_state.get_obs_val_col_titles_about_urls_for_csv(csv_url)
        )
        col_names_col_titles = data_cube_state.get_col_name_col_title_for_csv(csv_url)

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
            data_cube_state,
        )

        canonical_shape_dataset = melted_df.drop("Observation Value", axis=1)

    """
