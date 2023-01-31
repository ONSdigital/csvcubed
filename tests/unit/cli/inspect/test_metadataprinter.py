import pandas as pd
from pandas.testing import assert_frame_equal

from csvcubed.cli.inspect.metadataprinter import MetadataPrinter
from csvcubed.models.csvwtype import CSVWType
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.inspectdataframeresults import (
    DatasetObservationsByMeasureUnitInfoResult,
    DatasetObservationsInfoResult,
)
from csvcubed.models.sparqlresults import CodelistsResult
from csvcubed.utils.iterables import first
from tests.helpers.data_cube_state_cache import get_data_cube_state
from tests.unit.cli.inspect.test_inspectdatasetmanager import (
    expected_dataframe_pivoted_multi_measure,
    expected_dataframe_pivoted_single_measure,
)
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"

# TODO - change test name + give description
def test_multi_measure_pivoted_something_like_that():
    """ """
    path_to_json_file = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )

    data_cube_state = get_data_cube_state(path_to_json_file)
    metadata_printer = MetadataPrinter(data_cube_state)

    result_code_lists: CodelistsResult = metadata_printer.result_code_lists
    assert result_code_lists is not None

    assert len(result_code_lists.codelists) == 1
    assert (
        first(result_code_lists.codelists, lambda c: c.cols_used_in == "Some Dimension")
        is not None
    )

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
    assert type(expected_df.columns[0]) == type(
        result_dataset_value_counts.by_measure_and_unit_val_counts_df.columns[0]
    )
    assert_frame_equal(
        result_dataset_value_counts.by_measure_and_unit_val_counts_df, expected_df
    )


# TODO - change test name + give description
def test_single_measure_pivoted_something_like_that():
    """ """
    path_to_json_file = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )

    data_cube_state = get_data_cube_state(path_to_json_file)
    metadata_printer = MetadataPrinter(data_cube_state)

    result_code_lists: CodelistsResult = metadata_printer.result_code_lists
    assert result_code_lists is not None

    assert len(result_code_lists.codelists) == 1
    assert (
        first(result_code_lists.codelists, lambda c: c.cols_used_in == "Some Dimension")
        is not None
    )

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
