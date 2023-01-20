"""
CSV Dataset
-----------

Utilities for CSV Datasets
"""

from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from uuid import uuid1

import pandas as pd
import uritemplate
from csvcubedmodels.rdf.namespaces import SDMX_Attribute
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
    InvalidObservationColumnTitle,
    InvalidUnitColumnDefinition,
)
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import ColumnDefinition, QubeComponentResult
from csvcubed.utils.iterables import first
from csvcubed.utils.qb.components import ComponentField, ComponentPropertyType
from csvcubed.utils.sparql_handler.data_cube_state import DataCubeState


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
    column_definitions: List[ColumnDefinition],
    data_cube_state: DataCubeState,
    measure_uris: Set[str],
):
    """
    Adds the unit column to the melted data set for the pivoted shape data set input.
    """
    # Creating a new column in pandas dataframe with empty values.
    melted_df[col_name] = ""

    observed_value_columns = [
        c
        for c in column_definitions
        if c.property_url in measure_uris and c.data_type is not None
    ]

    unit_columns = [
        c
        for c in column_definitions
        if c.property_url == str(SDMX_Attribute.unitMeasure)
    ]

    for idx, row in melted_df.iterrows():
        observed_value_column = _get_observed_value_col_for_melted_df_row(
            observed_value_columns,
            row,
        )

        # Use the unit col's about url to get the unit col's value url.
        # N.B., for an old-style single measure pivoted shape, the following filter still works as the
        # about url and observation uri are both None (i.e. equal).

        unit_column = first(
            unit_columns, lambda u: u.about_url == observed_value_column.about_url
        )

        if unit_column is None or unit_column.value_url is None:
            raise InvalidUnitColumnDefinition(
                about_url=observed_value_column.about_url or "None",
                num_of_value_urls=0,
            )

        unit_uri = _get_unit_uri_for_maybe_template(
            unit_column.value_url, column_definitions, row
        )
        maybe_unit = data_cube_state.get_unit_for_uri(unit_uri)
        if maybe_unit is None:
            melted_df.loc[idx, col_name] = unit_uri
        else:
            melted_df.loc[idx, col_name] = maybe_unit.unit_label


def _get_unit_uri_for_maybe_template(
    template_url: str,
    column_definitions: List[ColumnDefinition],
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
            column_definitions,
            template_url,
            row,
        )


def _get_observed_value_col_for_melted_df_row(
    observation_value_columns: List[ColumnDefinition],
    row: pd.Series,
) -> ColumnDefinition:
    obs_val_col_title = str(row["Observation Value"])
    obs_val_column = first(
        observation_value_columns, lambda c: c.title == obs_val_col_title
    )
    if obs_val_column is None:
        raise InvalidObservationColumnTitle(obs_val_col_title=obs_val_col_title)
    return obs_val_column


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
            if obs_val_col_title in {col.title for col in comp.real_columns_used_in}
        ]

        if len(filtered_measure_components) != 1:
            raise InvalidNumOfDSDComponentsForObsValColTitleException(
                obs_val_col_title=obs_val_col_title,
                num_of_components=len(filtered_measure_components),
            )

        measure_component = filtered_measure_components[0]
        # Using the measure label if it exists as it is more user-friendly. Otherwise, we use the measure uri.
        melted_df.loc[idx, col_name] = (
            measure_component.property
            if measure_component.property_label is None
            else measure_component.property_label
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
        for c in measure_component.real_columns_used_in
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


def _get_unit_measure_col_for_standard_shape_cube(
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


def _melt_pivoted_shape(
    csv_url: str,
    data_cube_state: DataCubeState,
    qube_components: List[QubeComponentResult],
    canonical_shape_dataset: pd.DataFrame,
) -> Tuple[pd.DataFrame, str, str]:
    if csv_url is None:
        raise ValueError("csv_url cannot be None.")

    column_definitions = data_cube_state.get_column_definitions_for_csv(csv_url)

    measure_components = filter_components_from_dsd(
        qube_components,
        ComponentField.PropertyType,
        ComponentPropertyType.Measure.value,
    )
    measure_uris = {
        c.property
        for c in measure_components
        if c.property_type == str(ComponentPropertyType.Measure.value)
    }

    melted_df = _melt_data_set(canonical_shape_dataset, measure_components)

    measure_col = f"Measure_{str(uuid1())}"
    unit_col = f"Unit_{str(uuid1())}"
    _create_measure_col_in_melted_data_set_for_pivoted_shape(
        measure_col, melted_df, measure_components
    )
    _create_unit_col_in_melted_data_set_for_pivoted_shape(
        unit_col, melted_df, column_definitions, data_cube_state, measure_uris
    )

    canonical_shape_dataset = melted_df.drop("Observation Value", axis=1)

    return (canonical_shape_dataset, measure_col, unit_col)


def transform_dataset_to_canonical_shape(
    data_cube_state: DataCubeState,
    dataset: pd.DataFrame,
    csv_url: str,
    qube_components: List[QubeComponentResult],
) -> Tuple[pd.DataFrame, str, str]:
    """
    Transforms the given dataset into canonical shape if it is not in the canonical shape already.

    Member of :class:`./csvdataset`.

    :return: `Tuple[pd.DataFrame, str, str]` - canonical dataframe, measure column name, unit column name.
    """
    canonical_shape_dataset = dataset.copy()

    cube_shape = data_cube_state.get_shape_for_csv(csv_url)

    if cube_shape == CubeShape.Standard:
        return _get_unit_measure_col_for_standard_shape_cube(
            qube_components,
            data_cube_state,
            canonical_shape_dataset,
            data_cube_state.csvw_state.csvw_json_path,
        )
    else:
        # In pivoted shape
        return _melt_pivoted_shape(
            csv_url, data_cube_state, qube_components, canonical_shape_dataset
        )
