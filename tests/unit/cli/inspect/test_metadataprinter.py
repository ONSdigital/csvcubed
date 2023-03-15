import pandas as pd
from pandas.testing import assert_frame_equal

from csvcubed.cli.inspect.metadataprinter import MetadataPrinter
from csvcubed.models.csvwtype import CSVWType
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.cube.qb.validationerrors import BothMeasureTypesDefinedError
from csvcubed.models.inspectdataframeresults import (
    DatasetObservationsByMeasureUnitInfoResult,
    DatasetObservationsInfoResult,
)
from csvcubed.models.sparqlresults import CodelistsResult
from tests.helpers.inspectors_cache import get_data_cube_inspector
from tests.unit.cli.inspect.test_inspectdatasetmanager import (
    expected_dataframe_pivoted_multi_measure,
    expected_dataframe_pivoted_single_measure,
)
from tests.unit.test_baseunit import get_test_cases_dir
from tests.unit.utils.sparqlhandler.test_data_cube_inspector import (
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

    data_cube_inspector = get_data_cube_inspector(path_to_json_file)
    metadata_printer = MetadataPrinter(data_cube_inspector)

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

    data_cube_inspector = get_data_cube_inspector(path_to_json_file)
    metadata_printer = MetadataPrinter(data_cube_inspector)

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


def test_formatted_output():
    """This test checks the `_get_formated_output` outputs all the information correctly"""

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)

    (_, _, csv_url) = get_arguments_qb_dataset(data_cube_inspector)

    list_of_column_component_info = data_cube_inspector.get_column_component_info(
        csv_url
    )

    formatted_data = MetadataPrinter._get_formated_output(list_of_column_component_info)

    with open("Output.txt", "w") as text_file:
        text_file.write(formatted_data)
    text_file.close()

    with open("Output.txt", "r") as file:
        expected_output = file.read()
    file.close()

    assert formatted_data == expected_output
