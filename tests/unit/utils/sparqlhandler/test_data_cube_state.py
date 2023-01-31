from pathlib import Path

import pytest

from csvcubed.cli.inspect.metadataprinter import to_absolute_rdflib_file_path
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import ColumnDefinition, QubeComponentsResult
from csvcubed.utils.qb.components import ComponentPropertyType
from csvcubed.utils.sparql_handler.csvw_state import CsvWState
from csvcubed.utils.sparql_handler.data_cube_state import DataCubeState
from csvcubed.utils.sparql_handler.sparqlquerymanager import select_qb_csv_url
from csvcubed.utils.tableschema import CsvwRdfManager
from tests.helpers.data_cube_state_cache import get_data_cube_state
from tests.unit.test_baseunit import get_test_cases_dir
from tests.unit.utils.sparqlhandler.test_sparqlquerymanager import (
    assert_dsd_component_equal,
    get_dsd_component_by_property_url,
)

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def get_path_to_file(folder_name: str, file_name: str) -> Path:

    csvw_metadata_json_path = _test_case_base_dir / folder_name / file_name
    return csvw_metadata_json_path


def get_csv_rdf_manager(path_to_file: Path) -> CsvwRdfManager:

    return CsvwRdfManager(path_to_file)


csvw_rdf_manager = get_csv_rdf_manager(
    get_path_to_file("pivoted-single-measure-dataset", "qb-id-10004.csv-metadata.json")
)
data_cube_state = DataCubeState(csvw_rdf_manager.csvw_state)


def test_get_column_definitions_for_csv():
    """
    Ensures that the `ColumnDefinition`s with different property values can be correctly loaded from as CSV-W file.
    """

    results = {
        c.name: c
        for c in data_cube_state.get_column_definitions_for_csv("qb-id-10004.csv")
    }

    assert len(results) == 12

    """
    Testing: csv_url, name, property_url, required=True, suppress_output=False,
              title, value_url, virtual=False
    """
    assert results["some_dimension"] == ColumnDefinition(
        csv_url="qb-id-10004.csv",
        about_url=None,
        data_type=None,
        name="some_dimension",
        property_url="qb-id-10004.csv#dimension/some-dimension",
        required=True,
        suppress_output=False,
        title="Some Dimension",
        value_url="some-dimension.csv#{+some_dimension}",
        virtual=False,
    )

    """
    Testing: about_url, required=False
    """
    # Testing about_url + required: false
    assert results["some_attribute"] == ColumnDefinition(
        csv_url="qb-id-10004.csv",
        about_url="qb-id-10004.csv#obs/{some_dimension}@some-measure",
        data_type=None,
        name="some_attribute",
        property_url="qb-id-10004.csv#attribute/some-attribute",
        required=False,
        suppress_output=False,
        title="Some Attribute",
        value_url="qb-id-10004.csv#attribute/some-attribute/{+some_attribute}",
        virtual=False,
    )

    """
    Testing: data_type
    """
    assert results["some_obs_val"] == ColumnDefinition(
        csv_url="qb-id-10004.csv",
        about_url="qb-id-10004.csv#obs/{some_dimension}@some-measure",
        data_type="http://www.w3.org/2001/XMLSchema#decimal",
        name="some_obs_val",
        property_url="qb-id-10004.csv#measure/some-measure",
        required=True,
        suppress_output=False,
        title="Some Obs Val",
        value_url=None,
        virtual=False,
    )

    """
    Testing: virtual=True, suppress_output=True
    """
    assert results["virt_suppressed_test"] == ColumnDefinition(
        csv_url="qb-id-10004.csv",
        about_url="http://example.com/about",
        data_type=None,
        name="virt_suppressed_test",
        property_url="http://example.com/property",
        required=False,
        suppress_output=True,
        title=None,
        value_url="http://example.com/value",
        virtual=True,
    )


def test_exception_is_thrown_for_invalid_csv_url():
    """
    Ensures that an exception is thrown when a getter is provided an invalid csv url.
    """

    input_dict = {"a": 1, "b": 2}

    with pytest.raises(KeyError) as exception:
        assert data_cube_state._get_value_for_key("c", input_dict)

    assert "Could not find the definition for key 'c'" in str(exception.value)


def test_get_data_set_dsd_csv_url_for_csv_url():
    """
    Ensures that the valid data_set_dsd_and_csv_url_for_csv_url property is returned.
    """

    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_state.get_primary_catalog_metadata()
    )

    data_set_uri = primary_catalog_metadata.dataset_uri
    data_set_uri = to_absolute_rdflib_file_path(
        data_set_uri,
        get_path_to_file(
            "pivoted-single-measure-dataset", "qb-id-10004.csv-metadata.json"
        ),
    )
    csv_url = select_qb_csv_url(
        data_cube_state.csvw_state.rdf_graph, data_set_uri
    ).csv_url

    data_set_dsd_csv_url_result = data_cube_state.get_cube_identifiers_for_csv(csv_url)

    assert data_set_dsd_csv_url_result is not None
    assert data_set_dsd_csv_url_result.csv_url == "qb-id-10004.csv"
    assert data_set_dsd_csv_url_result.data_set_url == "qb-id-10004.csv#dataset"
    assert data_set_dsd_csv_url_result.dsd_uri == "qb-id-10004.csv#structure"


def test_get_dsd_qube_components_for_csv():
    """
    Ensures that the valid dsd_qube_components_for_csv property is returned.
    """

    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_state.get_primary_catalog_metadata()
    )

    data_set_uri = primary_catalog_metadata.dataset_uri
    data_set_uri = to_absolute_rdflib_file_path(
        data_set_uri,
        get_path_to_file(
            "pivoted-single-measure-dataset", "qb-id-10004.csv-metadata.json"
        ),
    )
    csv_url = select_qb_csv_url(
        data_cube_state.csvw_state.rdf_graph, data_set_uri
    ).csv_url

    result_qube_components = data_cube_state.get_dsd_qube_components_for_csv(csv_url)

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
        ["Some Dimension"],
        ["Some Obs Val"],
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
        ["Some Attribute"],
        ["Some Obs Val"],
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
        [],
        [],
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
        [],
        ["Some Obs Val"],
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
        ["Some Obs Val"],
        ["Some Obs Val"],
        "qb-id-10004.csv#structure",
        True,
    )


# 1003 csv from here on

csvw_rdf_manager2 = get_csv_rdf_manager(
    get_path_to_file("pivoted-multi-measure-dataset", "qb-id-10003.csv-metadata.json")
)
data_cube_state2 = DataCubeState(csvw_rdf_manager2.csvw_state)


def test_detect_csvw_shape_pivoted():
    """
    Ensures that the shape of the cube represented by the input metadata is correctly returned as Pivoted.
    """

    cube_shape = data_cube_state2.get_shape_for_csv("qb-id-10003.csv")
    assert cube_shape == CubeShape.Pivoted


csvw_rdf_manager3 = get_csv_rdf_manager(
    get_path_to_file(
        "single-unit_single-measure", "energy-trends-uk-total-energy.csv-metadata.json"
    )
)
data_cube_state3 = DataCubeState(csvw_rdf_manager3.csvw_state)


def test_detect_csvw_shape_standard():
    """
    Ensures that the shape of the cube represented by the input metadata is correctly returned as Standard.
    """

    cube_shape = data_cube_state3.get_shape_for_csv("energy-trends-uk-total-energy.csv")

    assert cube_shape == CubeShape.Standard


def test_get_cube_identifiers_for_data_set():
    """
    Ensures we can return cube identifiers from a given dataset_uri
    """

    cube_identifiers = data_cube_state3.get_cube_identifiers_for_data_set(
        data_cube_state3.csvw_state.get_primary_catalog_metadata().dataset_uri
    )

    assert cube_identifiers is not None
    assert cube_identifiers.csv_url == "energy-trends-uk-total-energy.csv"
    assert cube_identifiers.data_set_url == "energy-trends-uk-total-energy.csv#dataset"
    assert cube_identifiers.dsd_uri == "energy-trends-uk-total-energy.csv#structure"


def test_get_cube_identifiers_for_data_set_error():
    """
    Ensures we can return cube identifiers from a given dataset_uri
    """

    csv_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )

    with pytest.raises(KeyError) as exception:
        cube_identifers = data_cube_state3.get_cube_identifiers_for_data_set(
            data_set_uri=csv_path
        )
        assert cube_identifers is None

    assert (
        f"Could not find the data_set with URI '{to_absolute_rdflib_file_path(csv_path)}'."
    ) in str(exception.value)


def test_dsd_compomnents_multi_measure_pivoted_shape():
    """
    This function should replace behaviour tests
    """
    path_to_json_file = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )

    data_cube_state = get_data_cube_state(path_to_json_file)

    result_qube_components: QubeComponentsResult = (
        data_cube_state.get_dsd_qube_components_for_csv("qb-id-10003.csv")
    )

    components = result_qube_components.qube_components
    assert len(components) == 7

    component = get_dsd_component_by_property_url(
        components, "qb-id-10003.csv#dimension/some-dimension"
    )
    assert_dsd_component_equal(
        component,
        "qb-id-10003.csv#dimension/some-dimension",
        ComponentPropertyType.Dimension,
        "Some Dimension",
        ["Some Dimension"],
        ["Some Obs Val", "Some Other Obs Val"],
        "qb-id-10003.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(
        components, "qb-id-10003.csv#attribute/some-attribute"
    )
    assert_dsd_component_equal(
        component,
        "qb-id-10003.csv#attribute/some-attribute",
        ComponentPropertyType.Attribute,
        "Some Attribute",
        ["Some Attribute"],
        ["Some Obs Val"],
        "qb-id-10003.csv#structure",
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
        [],
        [],
        "qb-id-10003.csv#structure",
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
        ["Some Unit"],
        ["Some Other Obs Val", "Some Obs Val"],
        "qb-id-10003.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(
        components, "qb-id-10003.csv#measure/some-measure"
    )
    assert_dsd_component_equal(
        component,
        "qb-id-10003.csv#measure/some-measure",
        ComponentPropertyType.Measure,
        "Some Measure",
        ["Some Obs Val"],
        ["Some Obs Val"],
        "qb-id-10003.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(
        components, "qb-id-10003.csv#measure/some-other-measure"
    )
    assert_dsd_component_equal(
        component,
        "qb-id-10003.csv#measure/some-other-measure",
        ComponentPropertyType.Measure,
        "Some Other Measure",
        ["Some Other Obs Val"],
        ["Some Other Obs Val"],
        "qb-id-10003.csv#structure",
        True,
    )


def test_dsd_single_measure_pivoted_shape():

    path_to_json_file = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )

    data_cube_state = get_data_cube_state(path_to_json_file)

    result_qube_components: QubeComponentsResult = (
        data_cube_state.get_dsd_qube_components_for_csv("qb-id-10004.csv")
    )
    assert result_qube_components is not None

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
        ["Some Dimension"],
        ["Some Obs Val"],
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
        ["Some Attribute"],
        ["Some Obs Val"],
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
        [],
        [],
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
        [],
        ["Some Obs Val"],
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
        ["Some Obs Val"],
        ["Some Obs Val"],
        "qb-id-10004.csv#structure",
        True,
    )
