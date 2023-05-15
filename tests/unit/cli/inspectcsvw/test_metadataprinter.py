from typing import Dict, List

import pandas as pd
from pandas.testing import assert_frame_equal

from csvcubed.cli.inspectcsvw.metadataprinter import MetadataPrinter
from csvcubed.definitions import SDMX_ATTRIBUTE_UNIT_URI
from csvcubed.models.csvwtype import CSVWType
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.inspectdataframeresults import (
    DatasetObservationsByMeasureUnitInfoResult,
    DatasetObservationsInfoResult,
)
from csvcubed.models.sparqlresults import CodelistsResult
from tests.helpers.repository_cache import get_data_cube_repository
from tests.unit.cli.inspectcsvw.test_inspectdatasetmanager import (
    expected_dataframe_pivoted_multi_measure,
    expected_dataframe_pivoted_single_measure,
)
from tests.unit.test_baseunit import get_test_cases_dir
from tests.unit.utils.sparqlhandler.test_data_cube_repository import (
    get_arguments_qb_dataset,
)

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_multi_measure_pivoted_shape_cube_observation_and_count_info():
    """Testing the ability to return oberservation and count information for a
    multi measure pivoted cube (as opposed to a code-list)."""
    path_to_json_file = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )

    data_cube_repository = get_data_cube_repository(path_to_json_file)
    metadata_printer = MetadataPrinter(data_cube_repository)

    result_code_lists: CodelistsResult = metadata_printer.result_primary_csv_code_lists
    assert result_code_lists is not None

    assert len(result_code_lists.codelists) == 1
    assert result_code_lists.codelists[0].cols_used_in[0] == "Some Dimension"

    result_dataset_observations_info: DatasetObservationsInfoResult = (
        metadata_printer.result_dataset_observations_info
    )
    assert result_dataset_observations_info is not None
    assert result_dataset_observations_info.csvw_type == CSVWType.QbDataSet
    assert result_dataset_observations_info.cube_shape == CubeShape.Pivoted
    assert result_dataset_observations_info.num_of_observations == 3
    assert result_dataset_observations_info.num_of_duplicates == 0
    assert_frame_equal(
        result_dataset_observations_info.dataset_head,
        expected_dataframe_pivoted_multi_measure.head(n=3),
    )
    assert_frame_equal(
        result_dataset_observations_info.dataset_tail,
        expected_dataframe_pivoted_multi_measure.tail(n=3),
    )

    result_dataset_value_counts: DatasetObservationsByMeasureUnitInfoResult = (
        metadata_printer.result_dataset_value_counts
    )
    assert result_dataset_value_counts is not None

    expected_df = pd.DataFrame(
        [
            {
                "Measure": "Some Measure",
                "Unit": "Some Unit",
                "Count": 3,
            },
            {
                "Measure": "Some Other Measure",
                "Unit": "Percent",
                "Count": 3,
            },
        ]
    )
    assert result_dataset_value_counts.by_measure_and_unit_val_counts_df.empty == False
    assert_frame_equal(
        result_dataset_value_counts.by_measure_and_unit_val_counts_df, expected_df
    )


def test_single_measure_pivoted_shape_cube_observation_and_count_info():
    """Testing the ability to return oberservation and count information for a
    single measure pivoted cube (as opposed to a code-list)."""
    path_to_json_file = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )

    data_cube_repository = get_data_cube_repository(path_to_json_file)
    metadata_printer = MetadataPrinter(data_cube_repository)

    result_code_lists: CodelistsResult = metadata_printer.result_primary_csv_code_lists
    assert result_code_lists is not None

    assert len(result_code_lists.codelists) == 1
    assert result_code_lists.codelists[0].cols_used_in[0] == "Some Dimension"

    result_dataset_observations_info: DatasetObservationsInfoResult = (
        metadata_printer.result_dataset_observations_info
    )
    assert result_dataset_observations_info is not None
    assert result_dataset_observations_info.csvw_type == CSVWType.QbDataSet
    assert result_dataset_observations_info.cube_shape == CubeShape.Pivoted
    assert result_dataset_observations_info.num_of_observations == 3
    assert result_dataset_observations_info.num_of_duplicates == 0
    assert_frame_equal(
        result_dataset_observations_info.dataset_head,
        expected_dataframe_pivoted_single_measure.head(n=3),
    )
    assert_frame_equal(
        result_dataset_observations_info.dataset_tail,
        expected_dataframe_pivoted_single_measure.tail(n=3),
    )

    result_dataset_value_counts: DatasetObservationsByMeasureUnitInfoResult = (
        metadata_printer.result_dataset_value_counts
    )
    assert result_dataset_value_counts is not None

    expected_df = pd.DataFrame(
        [
            {
                "Measure": "Some Measure",
                "Unit": "Some Unit",
                "Count": 3,
            }
        ]
    )
    assert result_dataset_value_counts.by_measure_and_unit_val_counts_df.empty == False
    assert_frame_equal(
        result_dataset_value_counts.by_measure_and_unit_val_counts_df, expected_df
    )


def test_column_component_info_for_output():
    """This test checks the `_get_column_component_info_for_output` structures the information for output correctly."""

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )

    data_cube_repository = get_data_cube_repository(csvw_metadata_json_path)

    csv_url = data_cube_repository.get_primary_csv_url()

    list_of_column_component_info = data_cube_repository.get_column_component_info(
        csv_url
    )

    column_infos: List[
        Dict[str, str]
    ] = MetadataPrinter._get_column_component_info_for_output(
        list_of_column_component_info
    )

    assert column_infos == [
        {
            "Title": "Some Dimension",
            "Type": "Dimension",
            "Required": True,
            "Property URL": "qb-id-10003.csv#dimension/some-dimension",
            "Observations Column Titles": "Some Obs Val, Some Other Obs Val",
        },
        {
            "Title": "Some Attribute",
            "Type": "Attribute",
            "Required": False,
            "Property URL": "qb-id-10003.csv#attribute/some-attribute",
            "Observations Column Titles": "Some Obs Val",
        },
        {
            "Title": "Some Obs Val",
            "Type": "Observations",
            "Required": True,
            "Property URL": "qb-id-10003.csv#measure/some-measure",
            "Observations Column Titles": "Some Obs Val",
        },
        {
            "Title": "Some Other Obs Val",
            "Type": "Observations",
            "Required": True,
            "Property URL": "qb-id-10003.csv#measure/some-other-measure",
            "Observations Column Titles": "Some Other Obs Val",
        },
        {
            "Title": "Some Unit",
            "Type": "Units",
            "Required": True,
            "Property URL": SDMX_ATTRIBUTE_UNIT_URI,
            "Observations Column Titles": "Some Obs Val, Some Other Obs Val",
        },
    ]
