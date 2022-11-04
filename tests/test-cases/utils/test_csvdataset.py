import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal

from csvcubed.utils.csvdataset import transform_dataset_to_canonical_shape
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
            "Value": 221.4
        },
        {
            "Period": "year/1996",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 230.8
        },
        {
            "Period": "year/1997",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 224.5
        },
        {
            "Period": "year/1998",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 230.7
        },
        {
            "Period": "year/1999",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 231.4
        },
        {
            "Period": "year/2000",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 234.8
        },
        {
            "Period": "year/2001",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 236.9
        },
        {
            "Period": "year/2002",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 229.6
        },
        {
            "Period": "year/2003",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 231.9
        },
        {
            "Period": "year/2004",
            "Region": "K02000001",
            "Fuel": "all",
            "Measure Type": "energy-consumption",
            "Unit": "millions-of-tonnes-of-oil-equivalent",
            "Value": 233.7
        }
    ]
).replace("", np.NAN)

_expected_dataset_pivoted_single_measure_shape_cube = pd.DataFrame(
    [
        {}
    ]
)

_expected_dataset_pivoted_multi_measure_shape_cube = pd.DataFrame(
    [
        {}
    ]
)


def test_transform_to_canonical_shape_for_standard_shape_data_set():
    """
    TODO: Add description
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
        dataset,
        qube_components,
        dsd_uri,
        csvw_metadata_rdf_graph,
        csvw_metadata_json_path,
    )

    generated_dataset = canonical_shape_dataset.head(n=10)
    row = generated_dataset.iloc[9]

    assert_frame_equal(generated_dataset, _expected_dataset_standard_shape_cube)
    assert measure_col == "Measure Type"
    assert unit_col == "Unit"

def test_transform_to_canonical_shape_for_pivoted_single_measure_shape_data_set():
    """
    TODO: Add description
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
        dataset,
        qube_components,
        dsd_uri,
        csvw_metadata_rdf_graph,
        csvw_metadata_json_path,
    )
    
    assert_frame_equal(canonical_shape_dataset, _expected_dataset_pivoted_single_measure_shape_cube)
    assert measure_col == "Measure col name"
    assert unit_col == "Unit col name"

def test_transform_to_canonical_shape_for_pivoted_multi_measure_shape_data_set():
    """
    TODO: Add description
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
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
        dataset,
        qube_components,
        dsd_uri,
        csvw_metadata_rdf_graph,
        csvw_metadata_json_path,
    )

    assert_frame_equal(canonical_shape_dataset, _expected_dataset_pivoted_multi_measure_shape_cube)
    assert measure_col == "Measure col name"
    assert unit_col == "Unit col name"