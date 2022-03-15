from pandas import DataFrame
import pytest
from pandas.util.testing import assert_frame_equal
import numpy as np

from csvcubed.cli.inspect.inspectdatasetmanager import (
    get_dataset_observations_info,
    load_csv_to_dataframe,
)
from csvcubed.cli.inspect.metadataprocessor import MetadataProcessor
from csvcubed.models.inspectdataframeresults import DatasetObservationsInfoResult
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"
_expected_dataframe = DataFrame(
    [
        {
            "Label": "All",
            "Notation": "all",
            "Parent Notation": "",
            "Sort Priority": 0,
            "Description": "",
        },
        {
            "Label": "Ready to Drink",
            "Notation": "ready-to-drink",
            "Parent Notation": "",
            "Sort Priority": 1,
            "Description": "",
        },
        {
            "Label": "Sparkling",
            "Notation": "sparkling",
            "Parent Notation": "",
            "Sort Priority": 2,
            "Description": "",
        },
        {
            "Label": "Still",
            "Notation": "still",
            "Parent Notation": "",
            "Sort Priority": 3,
            "Description": "",
        },
        {
            "Label": "UK",
            "Notation": "uk",
            "Parent Notation": "",
            "Sort Priority": 4,
            "Description": "",
        },
        {
            "Label": "UK Grain and Blend",
            "Notation": "uk-grain-and-blend",
            "Parent Notation": "",
            "Sort Priority": 5,
            "Description": "",
        },
        {
            "Label": "UK Potable",
            "Notation": "uk-potable",
            "Parent Notation": "",
            "Sort Priority": 6,
            "Description": "",
        },
        {
            "Label": "UK Registered",
            "Notation": "uk-registered",
            "Parent Notation": None,
            "Sort Priority": 7,
            "Description": "",
        },
        {
            "Label": "Uk Malt",
            "Notation": "uk-malt",
            "Parent Notation": "",
            "Sort Priority": 8,
            "Description": "",
        },
        {
            "Label": "UK Registered",
            "Notation": "uk-registered",
            "Parent Notation": "",
            "Sort Priority": 7,
            "Description": "",
        },
        {
            "Label": "Uk Malt",
            "Notation": "uk-malt",
            "Parent Notation": "",
            "Sort Priority": 8,
            "Description": "",
        },
    ]
).replace("", np.NAN)


def test_load_csv_to_dataframe_success():
    """
    Should load the csv to dataframe successfully.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    dataset = load_csv_to_dataframe(csvw_metadata_json_path, "csv_file.csv")

    assert dataset is not None
    assert len(dataset.index) == 11
    assert_frame_equal(dataset, _expected_dataframe)


def test_load_csv_to_dataframe_error():
    """
    Should error when loading csv to dataframe.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"

    with pytest.raises(Exception):
        load_csv_to_dataframe(csvw_metadata_json_path, "missing_csv_file.csv")

def test_get_dataset_measure_type_single_measure():
    #TODO: FORM HERE
    #TODO: FORM HERE
    """
    Should return `DatasetMeasureType.SINGLE_MEASURE`.
    """
    assert True

def test_get_dataset_measure_type_multi_measure():
    """
    Should return `DatasetMeasureType.MULTI_MEASURE`.
    """
    assert True
    
def test_get_dataset_observations_info():
    """
    Should produce the expected `DatasetObservationsInfoResult`.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    dataset = load_csv_to_dataframe(csvw_metadata_json_path, "csv_file.csv")

    result: DatasetObservationsInfoResult = get_dataset_observations_info(dataset)

    assert result.num_of_observations == 11
    assert result.num_of_duplicates == 2
    assert_frame_equal(result.dataset_head, _expected_dataframe.head(n=10))
    assert_frame_equal(result.dataset_tail, _expected_dataframe.tail(n=10))

