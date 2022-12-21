import pytest
from csvcubed.cli.inspect.metadataprinter import to_absolute_rdflib_file_path
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import (
    ColTitlesAndNamesResult,
    ObservationValueColumnTitleAboutUrlResult,
    UnitColumnAboutValueUrlResult,
)
from csvcubed.utils.qb.components import ComponentPropertyType
from csvcubed.utils.sparql_handler.data_cube_state import DataCubeState
from csvcubed.utils.sparql_handler.sparqlquerymanager import (
    select_csvw_catalog_metadata,
    select_csvw_dsd_dataset_label_and_dsd_def_uri,
    select_qb_csv_url,
)
from csvcubed.utils.tableschema import CsvwRdfManager
from typing import List

from tests.unit.test_baseunit import get_test_cases_dir
from tests.unit.utils.sparqlhandler.test_sparqlquerymanager import get_dsd_component_by_property_url, assert_dsd_component_equal

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
    data_cube_state = DataCubeState(csvw_metadata_rdf_graph, CubeShape.Pivoted, csvw_metadata_json_path)

    data_set_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    data_set_uri = to_absolute_rdflib_file_path(data_set_uri, csvw_metadata_json_path)
    csv_url = select_qb_csv_url(
        csvw_metadata_rdf_graph, data_set_uri
    ).csv_url

    results = data_cube_state.get_unit_col_about_value_urls_for_csv(csv_url)

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
    data_cube_state = DataCubeState(csvw_metadata_rdf_graph, CubeShape.Pivoted, csvw_metadata_json_path)
    
    data_set_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    data_set_uri = to_absolute_rdflib_file_path(data_set_uri, csvw_metadata_json_path)
    csv_url = select_qb_csv_url(
        csvw_metadata_rdf_graph, data_set_uri
    ).csv_url

    results = data_cube_state.get_obs_val_col_titles_about_urls_for_csv(csv_url)

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
    data_cube_state = DataCubeState(csvw_metadata_rdf_graph, CubeShape.Pivoted, csvw_metadata_json_path)

    data_set_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    data_set_uri = to_absolute_rdflib_file_path(data_set_uri, csvw_metadata_json_path)
    csv_url = select_qb_csv_url(
        csvw_metadata_rdf_graph, data_set_uri
    ).csv_url

    results = data_cube_state.get_col_name_col_title_for_csv(csv_url)

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
    data_cube_state = DataCubeState(csvw_metadata_rdf_graph, CubeShape.Pivoted, csvw_metadata_json_path)

    input_dict = {"a": 1, "b": 2}

    with pytest.raises(ValueError) as exception:
        assert data_cube_state._get_value_for_key("c", input_dict)

    assert str(exception.value) == "Could not find the definition for key 'c'"

def test_get_data_set_dsd_csv_url_for_csv_url():
    """
    Ensures that the valid data_set_dsd_and_csv_url_for_csv_url property is returned.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph
    data_cube_state = DataCubeState(csvw_metadata_rdf_graph, CubeShape.Pivoted, csvw_metadata_json_path)

    data_set_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    data_set_uri = to_absolute_rdflib_file_path(data_set_uri, csvw_metadata_json_path)
    csv_url = select_qb_csv_url(
        csvw_metadata_rdf_graph, data_set_uri
    ).csv_url
    
    data_set_dsd_csv_url_result = data_cube_state.get_data_set_dsd_and_csv_url_for_csv_url(csv_url)
    
    assert data_set_dsd_csv_url_result is not None
    assert data_set_dsd_csv_url_result.csv_url == "qb-id-10004.csv"
    assert data_set_dsd_csv_url_result.data_set_url == "qb-id-10004.csv#dataset"
    assert data_set_dsd_csv_url_result.dsd_uri == "qb-id-10004.csv#structure"

def test_get_dsd_qube_components_for_csv():
    """
    Ensures that the valid dsd_qube_components_for_csv property is returned.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph
    data_cube_state = DataCubeState(csvw_metadata_rdf_graph, CubeShape.Pivoted, csvw_metadata_json_path)

    data_set_uri = select_csvw_catalog_metadata(csvw_metadata_rdf_graph).dataset_uri
    data_set_uri = to_absolute_rdflib_file_path(data_set_uri, csvw_metadata_json_path)
    csv_url = select_qb_csv_url(
        csvw_metadata_rdf_graph, data_set_uri
    ).csv_url
    
    result_data_set_dsd_csv_url = data_cube_state.get_data_set_dsd_and_csv_url_for_csv_url(csv_url)
    result_qube_components = data_cube_state.get_dsd_qube_components_for_csv(result_data_set_dsd_csv_url.dsd_uri, result_data_set_dsd_csv_url.csv_url)
    
    components = result_qube_components.qube_components
    assert len(components) == 5
    
    component = get_dsd_component_by_property_url(
        components, "qb-id-10004.csv#dimension/some-dimension"
    )
    assert_dsd_component_equal(
        component,
        "qb-id-10004.csv#dimension/some-dimension",
        ComponentPropertyType.Dimension,
        "Some Dimension",
        "Some Dimension",
        "Some Obs Val",
        "qb-id-10004.csv",
        "qb-id-10004.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(
        components, "qb-id-10004.csv#attribute/some-attribute"
    )
    assert_dsd_component_equal(
        component,
        "qb-id-10004.csv#attribute/some-attribute",
        ComponentPropertyType.Attribute,
        "Some Attribute",
        "Some Attribute",
        "Some Obs Val",
        "qb-id-10004.csv",
        "qb-id-10004.csv#structure",
        False,
    )

    component = get_dsd_component_by_property_url(
        components, "http://purl.org/linked-data/cube#measureType"
    )
    assert_dsd_component_equal(
        component,
        "http://purl.org/linked-data/cube#measureType",
        ComponentPropertyType.Dimension,
        "",
        "",
        "",
        "qb-id-10004.csv",
        "qb-id-10004.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(
        components, "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
    )
    assert_dsd_component_equal(
        component,
        "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure",
        ComponentPropertyType.Attribute,
        "",
        "",
        "Some Obs Val",
        "qb-id-10004.csv",
        "qb-id-10004.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(
        components, "qb-id-10004.csv#measure/some-measure"
    )
    assert_dsd_component_equal(
        component,
        "qb-id-10004.csv#measure/some-measure",
        ComponentPropertyType.Measure,
        "Some Measure",
        "Some Obs Val",
        "Some Obs Val",
        "qb-id-10004.csv",
        "qb-id-10004.csv#structure",
        True,
    )