import pytest
from csvcubed.cli.inspect.metadataprinter import to_absolute_rdflib_file_path
from csvcubed.models.sparqlresults import (
    ColTitlesAndNamesResult,
    ObservationValueColumnTitleAboutUrlResult,
    UnitColumnAboutValueUrlResult,
)
from csvcubed.utils.sparql_handler.data_cube_state import DataCubeState
from csvcubed.utils.sparql_handler.sparqlmanager import (
    select_csvw_catalog_metadata,
    select_qb_dataset_url,
)
from csvcubed.utils.tableschema import CsvwRdfManager
from typing import List

from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def _get_unit_col_about_value_urls_result_by_about_url(
    about_url: str, results: List[UnitColumnAboutValueUrlResult]
) -> UnitColumnAboutValueUrlResult:
    results = [result for result in results if result.about_url == about_url]
    assert len(results) == 1
    return results[0]


def _get_obs_val_col_title_about_url_result_by_about_url(
    about_url: str, results: List[ObservationValueColumnTitleAboutUrlResult]
) -> ObservationValueColumnTitleAboutUrlResult:
    results = [
        result
        for result in results
        if result.observation_value_col_about_url == about_url
    ]
    assert len(results) == 1
    return results[0]


def _get_col_name_col_title_result_by_col_name(
    column_name: str, results: List[ColTitlesAndNamesResult]
) -> ColTitlesAndNamesResult:
    results = [result for result in results if result.column_name == column_name]
    assert len(results) == 1
    return results[0]


def test_get_unit_col_about_value_urls_for_csv():
    """
    Ensures that the valid unit_col_about_value property is returned for the given csv.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    data_cube_state = DataCubeState(csvw_metadata_rdf_graph)

    data_set_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    data_set_uri = to_absolute_rdflib_file_path(data_set_uri, csvw_metadata_json_path)
    data_set_url = select_qb_dataset_url(
        csvw_metadata_rdf_graph, data_set_uri
    ).dataset_url

    results = data_cube_state.get_unit_col_about_value_urls_for_csv(data_set_url)

    assert len(results) == 1

    result = _get_unit_col_about_value_urls_result_by_about_url(
        "qb-id-10004.csv#obs/{some_dimension}@some-measure", results
    )
    print(type(result))
    assert result.csv_url == "qb-id-10004.csv"
    assert result.about_url == "qb-id-10004.csv#obs/{some_dimension}@some-measure"
    assert result.value_url == "qb-id-10004.csv#unit/some-unit"


def test_get_obs_val_col_title_about_url_for_csv():
    """
    Ensures that the valid obs_val_col_title_about_url_for_csv property is returned for the given csv.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    data_cube_state = DataCubeState(csvw_metadata_rdf_graph)

    data_set_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    data_set_uri = to_absolute_rdflib_file_path(data_set_uri, csvw_metadata_json_path)
    data_set_url = select_qb_dataset_url(
        csvw_metadata_rdf_graph, data_set_uri
    ).dataset_url

    results = data_cube_state.get_obs_val_col_titles_about_urls_for_csv(data_set_url)

    result = _get_obs_val_col_title_about_url_result_by_about_url(
        "qb-id-10004.csv#obs/{some_dimension}@some-measure", results
    )

    assert result.csv_url == "qb-id-10004.csv"
    assert result.observation_value_col_title == "Some Obs Val"
    assert (
        result.observation_value_col_about_url
        == "qb-id-10004.csv#obs/{some_dimension}@some-measure"
    )


def test_get_col_name_col_title_for_csv():
    """
    Ensures that the valid obs_val_col_title_about_url_for_csv property is returned for the given csv.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    data_cube_state = DataCubeState(csvw_metadata_rdf_graph)

    data_set_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    data_set_uri = to_absolute_rdflib_file_path(data_set_uri, csvw_metadata_json_path)
    data_set_url = select_qb_dataset_url(
        csvw_metadata_rdf_graph, data_set_uri
    ).dataset_url

    results = data_cube_state.get_col_name_col_title_for_csv(data_set_url)

    result = _get_col_name_col_title_result_by_col_name("some_dimension", results)
    result.column_name == "some_dimension"
    result.column_title == "Some Dimension"
    
    result = _get_col_name_col_title_result_by_col_name("some_attribute", results)
    result.column_name == "some_attribute"
    result.column_title == "Some Attribute"

    result = _get_col_name_col_title_result_by_col_name("some_obs_val", results)
    result.column_name == "some_obs_val"
    result.column_title == "Some Obs Val"

def test_exception_is_thrown_for_invalid_csv_url():
    """
    Ensures that an exception is thrown when a getter is provided an invalid csv url.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    data_cube_state = DataCubeState(csvw_metadata_rdf_graph)

    input_dict = {"a": 1, "b": 2}

    with pytest.raises(ValueError) as exception:
        assert data_cube_state._get_value_for_key("c", input_dict)

    assert str(exception.value) == "Could not find the definition for key 'c'"
