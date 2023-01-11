import numpy as np
import pandas as pd
import pytest
from pandas.util.testing import assert_frame_equal

from csvcubed.cli.inspect.metadataprinter import to_absolute_rdflib_file_path
from csvcubed.models.csvcubedexception import (
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
from csvcubed.utils.csvdataset import (
    _create_measure_col_in_melted_data_set_for_pivoted_shape,
    _create_unit_col_in_melted_data_set_for_pivoted_shape,
    _melt_data_set,
    transform_dataset_to_canonical_shape,
)
from csvcubed.utils.qb.components import ComponentPropertyType
from csvcubed.utils.sparql_handler.data_cube_state import DataCubeState
from csvcubed.utils.sparql_handler.sparqlquerymanager import (
    select_csvw_catalog_metadata,
    select_qb_csv_url,
)
from csvcubed.utils.tableschema import CsvwRdfManager
from tests.unit.cli.inspect.test_inspectdatasetmanager import get_arguments_qb_dataset
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"

_expected_dataset_standard_shape_cube = pd.DataFrame(
    [
        {
            "Period": "year/1995",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 221.4,
        },
        {
            "Period": "year/1996",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 230.8,
        },
        {
            "Period": "year/1997",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 224.5,
        },
        {
            "Period": "year/1998",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 230.7,
        },
        {
            "Period": "year/1999",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 231.4,
        },
        {
            "Period": "year/2000",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 234.8,
        },
        {
            "Period": "year/2001",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 236.9,
        },
        {
            "Period": "year/2002",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 229.6,
        },
        {
            "Period": "year/2003",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 231.9,
        },
        {
            "Period": "year/2004",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 233.7,
        },
    ]
).replace("", np.NAN)

_expected_dataset_pivoted_single_measure_shape_cube = pd.DataFrame(
    [
        {
            "Some Dimension": "a",
            "Some Attribute": "attr-a",
            "Value": 1,
            "Measure": "Some Measure",
            "Unit": "Some Unit",
        },
        {
            "Some Dimension": "b",
            "Some Attribute": "attr-b",
            "Value": 2,
            "Measure": "Some Measure",
            "Unit": "Some Unit",
        },
        {
            "Some Dimension": "c",
            "Some Attribute": "attr-c",
            "Value": 3,
            "Measure": "Some Measure",
            "Unit": "Some Unit",
        },
    ]
).replace("", np.NAN)
_expected_dataset_pivoted_single_measure_shape_cube = (
    _expected_dataset_pivoted_single_measure_shape_cube.reindex(
        ["Some Attribute", "Some Dimension", "Value", "Measure", "Unit"], axis=1
    )
)

_expected_dataset_pivoted_multi_measure_shape_cube = pd.DataFrame(
    [
        {
            "Some Attribute": "attr-a",
            "Some Dimension": "a",
            "Some Unit": "percent",
            "Value": 1,
            "Measure": "Some Measure",
            "Unit": "Some Unit",
        },
        {
            "Some Attribute": "attr-b",
            "Some Dimension": "b",
            "Some Unit": "percent",
            "Value": 2,
            "Measure": "Some Measure",
            "Unit": "Some Unit",
        },
        {
            "Some Attribute": "attr-c",
            "Some Dimension": "c",
            "Some Unit": "percent",
            "Value": 3,
            "Measure": "Some Measure",
            "Unit": "Some Unit",
        },
        {
            "Some Attribute": "attr-a",
            "Some Dimension": "a",
            "Some Unit": "percent",
            "Value": 2,
            "Measure": "Some Other Measure",
            "Unit": "Percent",
        },
        {
            "Some Attribute": "attr-b",
            "Some Dimension": "b",
            "Some Unit": "percent",
            "Value": 4,
            "Measure": "Some Other Measure",
            "Unit": "Percent",
        },
        {
            "Some Attribute": "attr-c",
            "Some Dimension": "c",
            "Some Unit": "percent",
            "Value": 6,
            "Measure": "Some Other Measure",
            "Unit": "Percent",
        },
    ]
).replace("", np.NAN)
_expected_dataset_pivoted_multi_measure_shape_cube = (
    _expected_dataset_pivoted_multi_measure_shape_cube.reindex(
        ["Some Attribute", "Some Dimension", "Some Unit", "Value", "Measure", "Unit"],
        axis=1,
    )
)

_expected_melted_dataset_for_pivoted_shape = pd.DataFrame(
    [
        {
            "Some Attribute": "attr-a",
            "Some Dimension": "a",
            "Some Unit": "percent",
            "Observation Value": "Some Obs Val",
            "Value": 1,
        },
        {
            "Some Attribute": "attr-b",
            "Some Dimension": "b",
            "Some Unit": "percent",
            "Observation Value": "Some Obs Val",
            "Value": 2,
        },
        {
            "Some Attribute": "attr-c",
            "Some Dimension": "c",
            "Some Unit": "percent",
            "Observation Value": "Some Obs Val",
            "Value": 3,
        },
        {
            "Some Attribute": "attr-a",
            "Some Dimension": "a",
            "Some Unit": "percent",
            "Observation Value": "Some Other Obs Val",
            "Value": 2,
        },
        {
            "Some Attribute": "attr-b",
            "Some Dimension": "b",
            "Some Unit": "percent",
            "Observation Value": "Some Other Obs Val",
            "Value": 4,
        },
        {
            "Some Attribute": "attr-c",
            "Some Dimension": "c",
            "Some Unit": "percent",
            "Observation Value": "Some Other Obs Val",
            "Value": 6,
        },
    ]
).replace("", np.NAN)
_expected_melted_dataset_for_pivoted_shape = (
    _expected_melted_dataset_for_pivoted_shape.reindex(
        ["Some Attribute", "Some Dimension", "Some Unit", "Observation Value", "Value"],
        axis=1,
    )
)

_expected_melted_dataset_with_measure_col_for_pivoted_shape = pd.DataFrame(
    [
        {
            "Some Attribute": "attr-a",
            "Some Dimension": "a",
            "Observation Value": "Some Obs Val",
            "Value": 1,
            "Measure": "Some Measure",
        },
        {
            "Some Attribute": "attr-b",
            "Some Dimension": "b",
            "Observation Value": "Some Obs Val",
            "Value": 2,
            "Measure": "Some Measure",
        },
        {
            "Some Attribute": "attr-c",
            "Some Dimension": "c",
            "Observation Value": "Some Obs Val",
            "Value": 3,
            "Measure": "Some Measure",
        },
        {
            "Some Attribute": "attr-a",
            "Some Dimension": "a",
            "Observation Value": "Some Other Obs Val",
            "Value": 2,
            "Measure": "Some Other Measure",
        },
        {
            "Some Attribute": "attr-b",
            "Some Dimension": "b",
            "Observation Value": "Some Other Obs Val",
            "Value": 4,
            "Measure": "Some Other Measure",
        },
        {
            "Some Attribute": "attr-c",
            "Some Dimension": "c",
            "Observation Value": "Some Other Obs Val",
            "Value": 6,
            "Measure": "Some Other Measure",
        },
    ]
).replace("", np.NAN)

_measure_components_for_multi_measure_pivoted_shape = [
    QubeComponentResult(
        "",
        "",
        "qb-id-10003.csv#measure/some-measure",
        "Some Measure",
        "Measure",
        "Some Obs Val",
        ComponentPropertyType.Measure.value,
        True,
    ),
    QubeComponentResult(
        "",
        "",
        "qb-id-10003.csv#measure/some-other-measure",
        "Some Other Measure",
        "Measure",
        "Some Other Obs Val",
        ComponentPropertyType.Measure.value,
        True,
    ),
]

_expected_dataset_pivoted_multi_measure_with_unit = pd.DataFrame(
    [
        {
            "Some Dimension": "a",
            "Some Attribute": "attr-a",
            "Some Unit": "percent",
            "Observation Value": "Some Obs Val",
            "Value": 1,
            "Unit": "Some Unit",
        },
        {
            "Some Dimension": "b",
            "Some Attribute": "attr-b",
            "Some Unit": "percent",
            "Observation Value": "Some Obs Val",
            "Value": 2,
            "Unit": "Some Unit",
        },
        {
            "Some Dimension": "c",
            "Some Attribute": "attr-c",
            "Some Unit": "percent",
            "Observation Value": "Some Obs Val",
            "Value": 3,
            "Unit": "Some Unit",
        },
        {
            "Some Attribute": "attr-a",
            "Some Dimension": "a",
            "Some Unit": "percent",
            "Observation Value": "Some Other Obs Val",
            "Value": 2,
            "Unit": "Percent",
        },
        {
            "Some Attribute": "attr-b",
            "Some Dimension": "b",
            "Some Unit": "percent",
            "Observation Value": "Some Other Obs Val",
            "Value": 4,
            "Unit": "Percent",
        },
        {
            "Some Attribute": "attr-c",
            "Some Dimension": "c",
            "Some Unit": "percent",
            "Observation Value": "Some Other Obs Val",
            "Value": 6,
            "Unit": "Percent",
        },
    ]
).replace("", np.NAN)
_expected_dataset_pivoted_multi_measure_with_unit = (
    _expected_dataset_pivoted_multi_measure_with_unit.reindex(
        [
            "Some Attribute",
            "Some Dimension",
            "Some Unit",
            "Observation Value",
            "Value",
            "Unit",
        ],
        axis=1,
    )
)

_unit_col_about_urls_value_urls = [
    UnitColumnAboutValueUrlResult(
        "qb-id-10004.csv",
        "qb-id-10003.csv#obs/some-dimension@some-measure",
        "qb-id-10003.csv#unit/some-unit",
    ),
    UnitColumnAboutValueUrlResult(
        "qb-id-10004.csv",
        "qb-id-10003.csv#obs/some-dimension@some-other-measure",
        "qb-id-10003.csv#unit/percent",
    ),
]

_obs_val_col_titles_about_urls = [
    ObservationValueColumnTitleAboutUrlResult(
        "qb-id-10004.csv",
        "Some Obs Val",
        "qb-id-10003.csv#obs/some-dimension@some-measure",
    ),
    ObservationValueColumnTitleAboutUrlResult(
        "qb-id-10004.csv",
        "Some Other Obs Val",
        "qb-id-10003.csv#obs/some-dimension@some-other-measure",
    ),
]

_col_names_col_titles = [
    ColTitlesAndNamesResult("qb-id-10004.csv", "some_dimension", "Some Dimension"),
    ColTitlesAndNamesResult("qb-id-10004.csv", "some_attribute", "Some Attribute"),
    ColTitlesAndNamesResult("qb-id-10004.csv", "some_obs_val", "Some Obs Val"),
    ColTitlesAndNamesResult(
        "qb-id-10004.csv", "some_other_obs_val", "Some Other Obs Val"
    ),
    ColTitlesAndNamesResult("qb-id-10004.csv", "some_unit", "Some Unit"),
]

_obs_val_col_titles_about_urls_invalid = [
    ObservationValueColumnTitleAboutUrlResult(
        "qb-id-10004.csv",
        "Some Obs Val",
        "qb-id-10003.csv#obs/some-dimension@some-measure",
    ),
    ObservationValueColumnTitleAboutUrlResult(
        "qb-id-10004.csv",
        "Some Obs Val",
        "qb-id-10003.csv#obs/some-dimension@some-other-measure",
    ),
]

_unit_col_about_urls_value_urls_invalid = [
    UnitColumnAboutValueUrlResult(
        "qb-id-10004.csv",
        "qb-id-10003.csv#obs/some-dimension@some-measure",
        "qb-id-10003.csv#unit/some-unit",
    ),
    UnitColumnAboutValueUrlResult(
        "qb-id-10004.csv",
        "qb-id-10003.csv#obs/some-dimension@some-measure",
        "qb-id-10003.csv#unit/percent",
    ),
]

_col_names_col_titles_invalid = [
    ColTitlesAndNamesResult("qb-id-10004.csv", "some_dimension", "Some Dimension"),
    ColTitlesAndNamesResult(
        "qb-id-10004.csv", "some_dimension", "Some Other Dimension"
    ),
    ColTitlesAndNamesResult("qb-id-10004.csv", "some_attribute", "Some Attribute"),
    ColTitlesAndNamesResult("qb-id-10004.csv", "some_obs_val", "Some Obs Val"),
    ColTitlesAndNamesResult("qb-id-10004.csv", "some_unit", "Some Other Obs Val"),
    ColTitlesAndNamesResult("qb-id-10004.csv", "some_unit", "Some Unit"),
]

_measure_components_for_multi_measure_pivoted_shape_same_measure = [
    QubeComponentResult(
        "",
        "",
        "qb-id-10003.csv#measure/some-measure",
        "Some Measure",
        "Measure",
        "Some Obs Val",
        ComponentPropertyType.Measure.value,
        True,
    ),
    QubeComponentResult(
        "",
        "",
        "qb-id-10003.csv#measure/some-other-measure",
        "Some Other Measure",
        "Measure",
        "Some Obs Val",
        ComponentPropertyType.Measure.value,
        True,
    ),
]


def test_transform_to_canonical_shape_for_standard_shape_data_set():
    """
    Ensures that the correct canonical shape data set is generated for the standard shape data set.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph
    data_cube_state = DataCubeState(csvw_metadata_rdf_graph, csvw_metadata_json_path)

    (dataset, qube_components, csv_url) = get_arguments_qb_dataset(data_cube_state)
    (
        canonical_shape_dataset,
        measure_col,
        unit_col,
    ) = transform_dataset_to_canonical_shape(
        data_cube_state,
        dataset,
        qube_components,
        csv_url,
        csvw_metadata_json_path,
    )

    generated_dataset = canonical_shape_dataset.head(n=10)

    assert measure_col == "Measure Type"
    assert unit_col == "Unit"
    assert_frame_equal(generated_dataset, _expected_dataset_standard_shape_cube)


def test_transform_to_canonical_shape_for_pivoted_single_measure_shape_data_set():
    """
    Ensures that the correct canonical shape data set is generated for the pivoted shape single measure data set.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph
    data_cube_state = DataCubeState(csvw_metadata_rdf_graph, csvw_metadata_json_path)

    (dataset, qube_components, csv_url) = get_arguments_qb_dataset(data_cube_state)

    (
        canonical_shape_dataset,
        measure_col,
        unit_col,
    ) = transform_dataset_to_canonical_shape(
        data_cube_state,
        dataset,
        qube_components,
        csv_url,
        csvw_metadata_json_path,
    )

    assert "Measure" in measure_col
    assert "Unit" in unit_col

    canonical_shape_dataset = canonical_shape_dataset.reindex(
        ["Some Attribute", "Some Dimension", "Value", measure_col, unit_col], axis=1
    )
    _expected_dataset_pivoted_single_measure_shape_cube.rename(
        columns={
            "Measure": measure_col,
            "Unit": unit_col,
        },
        inplace=True,
    )
    assert_frame_equal(
        canonical_shape_dataset, _expected_dataset_pivoted_single_measure_shape_cube
    )


def test_transform_to_canonical_shape_for_pivoted_multi_measure_shape_data_set():
    """
    Ensures that the correct canonical shape data set is generated for the pivoted shape multi measure data set.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph
    data_cube_state = DataCubeState(csvw_metadata_rdf_graph, csvw_metadata_json_path)

    (dataset, qube_components, csv_url) = get_arguments_qb_dataset(data_cube_state)

    (
        canonical_shape_dataset,
        measure_col,
        unit_col,
    ) = transform_dataset_to_canonical_shape(
        data_cube_state,
        dataset,
        qube_components,
        csv_url,
        csvw_metadata_json_path,
    )

    assert "Measure" in measure_col
    assert "Unit" in unit_col

    canonical_shape_dataset = canonical_shape_dataset.reindex(
        [
            "Some Attribute",
            "Some Dimension",
            "Some Unit",
            "Value",
            measure_col,
            unit_col,
        ],
        axis=1,
    )
    _expected_dataset_pivoted_multi_measure_shape_cube.rename(
        columns={
            "Measure": measure_col,
            "Unit": unit_col,
        },
        inplace=True,
    )
    assert_frame_equal(
        canonical_shape_dataset, _expected_dataset_pivoted_multi_measure_shape_cube
    )


def test_melt_data_set_for_pivoted_shape():
    """
    Ensures that a melted DataFrame output by _melt_data_set() is as expected.
    """
    test_csv_file = (
        _test_case_base_dir / "pivoted-multi-measure-dataset" / "qb-id-10003.csv"
    )
    pivoted_df = pd.read_csv(test_csv_file)
    melted_df = _melt_data_set(
        pivoted_df, _measure_components_for_multi_measure_pivoted_shape
    )

    assert melted_df is not None
    # Asserting the number of rows in the melted dataframe
    assert melted_df.shape[0] == 6
    # Asserting the number of columns in the melted dataframe
    assert melted_df.shape[1] == 5
    # Asserting the columns and data in the melted dataframe.
    melted_df = melted_df.reindex(
        ["Some Attribute", "Some Dimension", "Some Unit", "Observation Value", "Value"],
        axis=1,
    )
    assert_frame_equal(melted_df, _expected_melted_dataset_for_pivoted_shape)


def test_create_measure_col_in_melted_data_set_for_pivoted_shape():
    """
    Ensures that the correct measure column information is added to the melted dataframe.
    """
    test_csv_file = (
        _test_case_base_dir / "pivoted-multi-measure-dataset" / "qb-id-10003.csv"
    )
    pivoted_df = pd.read_csv(test_csv_file)
    melted_df = _melt_data_set(
        pivoted_df, _measure_components_for_multi_measure_pivoted_shape
    )

    _create_measure_col_in_melted_data_set_for_pivoted_shape(
        "Measure", melted_df, _measure_components_for_multi_measure_pivoted_shape
    )

    assert melted_df is not None
    # assert whether the melted_df_with_measure_col has the correct number of rows
    assert melted_df.shape[0] == 6
    # assert whether the melted_df_with_measure_col has the correct number of columns.
    assert melted_df.shape[1] == 6
    # assert whether the melted_df_with_measure_col dataframe equals to the expected dataframe.
    melted_df = melted_df.reindex(
        ["Some Attribute", "Some Dimension", "Observation Value", "Value", "Measure"],
        axis=1,
    )
    assert_frame_equal(
        melted_df, _expected_melted_dataset_with_measure_col_for_pivoted_shape
    )


def test_create_measure_in_melted_data_set_exception_for_more_than_one_matching_component_results():
    """
    Ensure that if there is more than one matching measure component that an exception is raised
    """

    test_csv_file = (
        _test_case_base_dir / "pivoted-multi-measure-dataset" / "qb-id-10003.csv"
    )
    pivoted_df = pd.read_csv(test_csv_file)
    melted_df = _melt_data_set(
        pivoted_df, _measure_components_for_multi_measure_pivoted_shape_same_measure
    )

    with pytest.raises(
        InvalidNumOfDSDComponentsForObsValColTitleException
    ) as exception:
        _create_measure_col_in_melted_data_set_for_pivoted_shape(
            "Measure",
            melted_df,
            _measure_components_for_multi_measure_pivoted_shape_same_measure,
        )
    assert (
        str(exception.value)
        == f"There should be only 1 component for the observation value column with title 'Some Obs Val', but found 2."
    )


def test_create_unit_col_in_melted_data_set_for_pivoted_shape():
    """
    Ensures that the correct unit column information is added to the melted dataframe.
    """
    test_csv_file = (
        _test_case_base_dir / "pivoted-multi-measure-dataset" / "qb-id-10003.csv"
    )
    pivoted_df = pd.read_csv(test_csv_file)
    melted_df = _melt_data_set(
        pivoted_df, _measure_components_for_multi_measure_pivoted_shape
    )

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    data_cube_state = DataCubeState(csvw_metadata_rdf_graph, csvw_metadata_json_path)

    _create_unit_col_in_melted_data_set_for_pivoted_shape(
        "Unit",
        melted_df,
        _unit_col_about_urls_value_urls,
        _obs_val_col_titles_about_urls,
        _col_names_col_titles,
        data_cube_state,
    )

    assert melted_df is not None
    # assert whether the melted_df_with_unit_col has the correct number of rows
    assert melted_df.shape[0] == 6
    # assert whether the melted_df_with_unit_col has the correct number of columns.
    assert melted_df.shape[1] == 6
    # assert whether the melted_df_with_unit_col dataframe equals to the expected dataframe.
    melted_df = melted_df.reindex(
        [
            "Some Attribute",
            "Some Dimension",
            "Some Unit",
            "Observation Value",
            "Value",
            "Unit",
        ],
        axis=1,
    )
    assert_frame_equal(melted_df, _expected_dataset_pivoted_multi_measure_with_unit)


def test_create_unit_col_in_melted_data_set_for_pivoted_shape_should_throw_invalid_num_of_unit_cols_exception():
    """
    Ensures the InvalidNumOfUnitColsForObsValColTitleException is thrown.
    """
    test_csv_file = (
        _test_case_base_dir / "pivoted-multi-measure-dataset" / "qb-id-10003.csv"
    )
    pivoted_df = pd.read_csv(test_csv_file)
    melted_df = _melt_data_set(
        pivoted_df, _measure_components_for_multi_measure_pivoted_shape
    )

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    data_cube_state = DataCubeState(csvw_metadata_rdf_graph, csvw_metadata_json_path)

    with pytest.raises(InvalidNumOfUnitColsForObsValColTitleException) as exception:
        _create_unit_col_in_melted_data_set_for_pivoted_shape(
            "Unit",
            melted_df,
            _unit_col_about_urls_value_urls,
            _obs_val_col_titles_about_urls_invalid,
            _col_names_col_titles,
            data_cube_state,
        )

    assert (
        str(exception.value)
        == "There should be 1 unit column for the observation value column title 'Some Other Obs Val', but found 0 unit columns."
    )


def test_create_unit_col_in_melted_data_set_for_pivoted_shape_should_throw_invalid_num_of_val_urls_exception():
    """
    Ensures the InvalidNumOfValUrlsForAboutUrlException is thrown.
    """
    test_csv_file = (
        _test_case_base_dir / "pivoted-multi-measure-dataset" / "qb-id-10003.csv"
    )
    pivoted_df = pd.read_csv(test_csv_file)
    melted_df = _melt_data_set(
        pivoted_df, _measure_components_for_multi_measure_pivoted_shape
    )

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    data_cube_state = DataCubeState(csvw_metadata_rdf_graph, csvw_metadata_json_path)

    with pytest.raises(InvalidNumOfValUrlsForAboutUrlException) as exception:
        _create_unit_col_in_melted_data_set_for_pivoted_shape(
            "Unit",
            melted_df,
            _unit_col_about_urls_value_urls_invalid,
            _obs_val_col_titles_about_urls,
            _col_names_col_titles,
            data_cube_state,
        )

    assert (
        str(exception.value)
        == "There should be only 1 value url for the about url 'qb-id-10003.csv#obs/some-dimension@some-other-measure', but found 0."
    )


def test_unit_not_defined_locally():
    """
    This function tests if the unit colum is not locally defined (so by that an external URL is used), and the label does not exist the
    URI will be used instead.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "unit_not_locally_defined.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    data_cube_state = DataCubeState(csvw_rdf_manager.rdf_graph, csvw_metadata_json_path)

    (dataset, qube_components, csv_url) = get_arguments_qb_dataset(data_cube_state)

    (
        canonical_shape_dataset,
        measure_col,
        unit_col,
    ) = transform_dataset_to_canonical_shape(
        data_cube_state,
        dataset,
        qube_components,
        csv_url,
        csvw_metadata_json_path,
    )

    unit_values = [
        "http://example.com/units/some-unit",
        "http://example.com/units/some-unit",
        "http://example.com/units/some-unit",
        "http://example.com/units/percent",
        "http://example.com/units/percent",
        "http://example.com/units/percent",
    ]
    assert list(canonical_shape_dataset[unit_col]) == unit_values
