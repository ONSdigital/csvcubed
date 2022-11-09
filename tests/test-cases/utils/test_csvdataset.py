import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal
from csvcubed.cli.inspect.inspectdatasetmanager import filter_components_from_dsd
from csvcubed.models.sparqlresults import QubeComponentResult

from csvcubed.utils.csvdataset import (
    _melt_data_set,
    transform_dataset_to_canonical_shape,
)
from csvcubed.utils.qb.components import ComponentField, ComponentPropertyType
from csvcubed.utils.sparql_handler.sparqlmanager import CSVWShape
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
            "Some Obs Val": 1,
            "Unit": "Some Unit",
            "Measure": "Some Measure",
        },
        {
            "Some Dimension": "b",
            "Some Attribute": "attr-b",
            "Some Obs Val": 2,
            "Unit": "Some Unit",
            "Measure": "Some Measure",
        },
        {
            "Some Dimension": "c",
            "Some Attribute": "attr-c",
            "Some Obs Val": 3,
            "Unit": "Some Unit",
            "Measure": "Some Measure",
        },
    ]
).replace("", np.NAN)

_expected_dataset_pivoted_multi_measure_shape_cube = pd.DataFrame([{}])

_expected_melted_dataset_for_pivoted_shape = pd.DataFrame(
        [
            {   
                "Some Attribute": "attr-a",
                "Some Dimension": "a",
                "Observation Value": "Some Obs Val",
                "Value": 1
            },

            {   
                "Some Attribute": "attr-b",
                "Some Dimension": "b",
                "Observation Value": "Some Obs Val",
                "Value": 2
            },

            {   
                "Some Attribute": "attr-c",
                "Some Dimension": "c",
                "Observation Value": "Some Obs Val",
                "Value": 3
            },

            {   
                "Some Attribute": "attr-a",
                "Some Dimension": "a",
                "Observation Value": "Some Other Obs Val",
                "Value": 2
            },

            {   
                "Some Attribute": "attr-b",
                "Some Dimension": "b",
                "Observation Value": "Some Other Obs Val",
                "Value": 4
            },

            {   
                "Some Attribute": "attr-c",
                "Some Dimension": "c",
                "Observation Value": "Some Other Obs Val",
                "Value": 6
            },
        ]
).replace("", np.NAN)


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

    (dataset, qube_components, dsd_uri, _) = get_arguments_qb_dataset(
        CSVWShape.Standard, csvw_metadata_rdf_graph, csvw_metadata_json_path
    )
    (
        canonical_shape_dataset,
        measure_col,
        unit_col,
    ) = transform_dataset_to_canonical_shape(
        CSVWShape.Standard,
        dataset,
        qube_components,
        dsd_uri,
        csvw_metadata_rdf_graph,
        csvw_metadata_json_path,
    )

    generated_dataset = canonical_shape_dataset.head(n=10)

    assert_frame_equal(generated_dataset, _expected_dataset_standard_shape_cube)
    assert measure_col == "Measure Type"
    assert unit_col == "Unit"


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

    (dataset, qube_components, dsd_uri, _) = get_arguments_qb_dataset(
        CSVWShape.Pivoted, csvw_metadata_rdf_graph, csvw_metadata_json_path
    )
    (
        canonical_shape_dataset,
        measure_col,
        unit_col,
    ) = transform_dataset_to_canonical_shape(
        CSVWShape.Pivoted,
        dataset,
        qube_components,
        dsd_uri,
        csvw_metadata_rdf_graph,
        csvw_metadata_json_path,
    )

    _expected_dataset_pivoted_single_measure_shape_cube.rename(
        columns={
            "Measure": measure_col,
            "Unit": unit_col,
        },
        inplace=True,
    )

    assert "Measure" in measure_col
    assert "Unit" in unit_col
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

    (dataset, qube_components, dsd_uri, _) = get_arguments_qb_dataset(
        CSVWShape.Pivoted, csvw_metadata_rdf_graph, csvw_metadata_json_path
    )
    (
        canonical_shape_dataset,
        measure_col,
        unit_col,
    ) = transform_dataset_to_canonical_shape(
        CSVWShape.Pivoted,
        dataset,
        qube_components,
        dsd_uri,
        csvw_metadata_rdf_graph,
        csvw_metadata_json_path,
    )

    assert measure_col == "Measure col name"
    assert unit_col == "Unit col name"

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
    df = pd.read_csv(test_csv_file)

    measure_components = [
        QubeComponentResult(
            "qb-id-10003.csv#measure/some-measure",
            "Some Measure",
            "Measure",
            "Some Obs Val",
            ComponentPropertyType.Measure.value,
            True,
        ),
        QubeComponentResult(
            "qb-id-10003.csv#measure/some-other-measure",
            "Some Other Measure",
            "Measure",
            "Some Other Obs Val",
            ComponentPropertyType.Measure.value,
            True,
        ),
    ]

    melted_df = _melt_data_set(df, measure_components)

    assert melted_df is not None
    # Asserting the number of rows in the melted dataframe
    assert melted_df.shape[0] == 6
    # Asserting the number of columns in the melted dataframe
    assert melted_df.shape[1] == 4
    # Asserting the columns and data in the melted dataframe.
    assert_frame_equal(melted_df, _expected_melted_dataset_for_pivoted_shape)
