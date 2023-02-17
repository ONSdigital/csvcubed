import pytest

from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import (
    CodelistResult,
    CodelistsResult,
    ColumnDefinition,
    CubeTableIdentifiers,
    QubeComponentsResult,
    UnitResult,
)
from csvcubed.utils.iterables import first
from csvcubed.utils.qb.components import ComponentPropertyType
from tests.helpers.inspectors_cache import get_csvw_rdf_manager, get_data_cube_inspector
from tests.unit.test_baseunit import get_test_cases_dir
from tests.unit.utils.sparqlhandler.test_sparqlquerymanager import (
    assert_dsd_component_equal,
    get_dsd_component_by_property_url,
)

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_get_column_definitions_for_csv():
    """
    Ensures that the `ColumnDefinition`s with different property values can be correctly loaded from as CSV-W file.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_state.get_primary_catalog_metadata()
    )
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    results = {
        c.name: c for c in data_cube_inspector.get_column_definitions_for_csv(csv_url)
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
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)

    with pytest.raises(KeyError) as exception:
        assert data_cube_inspector.get_cube_identifiers_for_csv("c")

    assert "Couldn't find value for key" in str(exception.value)


# Duplicate test
def test_get_cube_identifiers_for_data_set_error():
    """
    Ensures we can return the correct error message when attempting to return the
    cube identifiers from a given (incorrect) dataset_uri.
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)

    with pytest.raises(KeyError) as exception:
        cube_identifers = data_cube_inspector.get_cube_identifiers_for_data_set(
            data_set_uri=""
        )
        assert cube_identifers is None

    assert (f"Could not find the data_set with URI ''.") in str(exception.value)


def test_get_cube_identifiers_for_csv():
    """
    Ensures that the valid data_set_dsd_and_csv_url_for_csv_url property is returned.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )

    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_state.get_primary_catalog_metadata()
    )

    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    result: CubeTableIdentifiers = data_cube_inspector.get_cube_identifiers_for_csv(
        csv_url
    )

    assert result is not None
    assert result.csv_url == "qb-id-10004.csv"
    assert result.data_set_label == "Pivoted Shape Cube"
    assert result.data_set_url == "qb-id-10004.csv#dataset"
    assert result.dsd_uri == "qb-id-10004.csv#structure"


def test_get_cube_identifiers_for_data_set():
    """
    Ensures that the valid data_set_dsd_and_csv_url_for_data_set property is returned.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)

    primary_catalog_metadata = (
        data_cube_inspector.csvw_state.get_primary_catalog_metadata()
    )

    data_set_uri = primary_catalog_metadata.dataset_uri
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        data_set_uri
    ).csv_url

    result_qube_components = data_cube_inspector.get_dsd_qube_components_for_csv(
        csv_url
    )

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


def test_detect_csvw_shape_pivoted():
    """
    Ensures that the shape of the cube represented by the input metadata is correctly returned as Pivoted.
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_state.get_primary_catalog_metadata()
    )
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    cube_shape: CubeShape = data_cube_inspector.get_shape_for_csv(csv_url)

    assert cube_shape == CubeShape.Pivoted


def test_detect_csvw_shape_standard():
    """
    Ensures that the shape of the cube represented by the input metadata is correctly returned as Standard.
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_state.get_primary_catalog_metadata()
    )
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    cube_shape: CubeShape = data_cube_inspector.get_shape_for_csv(csv_url)

    assert cube_shape == CubeShape.Standard


def test_get_code_lists_and_cols():
    """
    Ensures that the correct codelists and associated columns represented by the input metadata are returned
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_state.get_primary_catalog_metadata()
    )
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    results = {
        c.csv_url: c
        for c in data_cube_inspector.get_code_lists_and_cols(csv_url).codelists
    }

    assert len(results) == 1
    assert results["qb-id-10004.csv"] == CodelistResult(
        code_list="some-dimension.csv#code-list",
        code_list_label="Some Dimension",
        cols_used_in=["Some Dimension"],
        csv_url=csv_url,
    )


def test_get_dsd_code_list_and_cols_without_codelist_labels():
    """
    Should return expected `DSDLabelURIResult`.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_state.get_primary_catalog_metadata()
    )
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    result: CodelistsResult = data_cube_inspector.get_code_lists_and_cols(csv_url)

    assert len(result.codelists) == 3
    assert (
        first(result.codelists, lambda c: c.cols_used_in == ["Alcohol Sub Type"])
        is not None
    )


def test_get_units():
    """
    Ensures that the correct unit uris and labels for the input metadata are returned
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)

    results = data_cube_inspector.get_units()

    unit_uris = {"qb-id-10003.csv#unit/percent", "qb-id-10003.csv#unit/some-unit"}
    results_unit_uris = {result.unit_uri for result in results}

    unit_labels = {"Percent", "Some Unit"}
    results_unit_labels = {result.unit_label for result in results}

    assert len(results) == 2
    assert unit_uris == results_unit_uris
    assert unit_labels == results_unit_labels


def test_get_unit_for_uri():
    """
    Ensures that the correct unit label is returned for the input metadata unit uri
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)

    result: UnitResult = data_cube_inspector.get_unit_for_uri(
        "qb-id-10003.csv#unit/percent"
    )

    assert result.unit_label == "Percent"
    assert result.unit_uri == "qb-id-10003.csv#unit/percent"


def test_get_suppressed_columns_for_csv():
    """
    Ensures that suppressed columns are correctly identified for the given csv_url
    """
    csvw_metadata_json_path = (
        _test_case_base_dir / "datacube_with_suppress_output_cols.csv-metadata.json"
    )
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)

    results = set(
        data_cube_inspector.get_suppressed_columns_for_csv(
            "multi-unit_multi-measure/alcohol-bulletin.csv"
        )
    )

    suppressed_columns = {"Col1WithSuppressOutput", "Col2WithSuppressOutput"}
    assert results == suppressed_columns


def test_get_suppressed_columns_when_no_columns_suppressed():
    """
    Tests if the get_suppressed_columns function successfully detects no suppressed columns when none are present.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_state.get_primary_catalog_metadata()
    )
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    result = data_cube_inspector.get_suppressed_columns_for_csv(csv_url)

    assert len(result) == 0


def test_get_dsd_qube_components_for_csv_multi_measure_pivoted():
    """
    Test that dsd components from a pivoted multi measure dataset are
    correctly returned by the inspector function get_dsd_qube_components_for_csv
    """
    path_to_json_file = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(path_to_json_file)
    data_cube_inspector = get_data_cube_inspector(path_to_json_file)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_state.get_primary_catalog_metadata()
    )
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    result_qube_components: QubeComponentsResult = (
        data_cube_inspector.get_dsd_qube_components_for_csv(csv_url)
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


def test_get_dsd_qube_components_for_csv_single_measure_pivoted():
    """
    Ensures that the valid dsd_qube_components_for_csv property is returned.
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )

    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_state.get_primary_catalog_metadata()
    )
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    result: QubeComponentsResult = data_cube_inspector.get_dsd_qube_components_for_csv(
        csv_url
    )

    components = result.qube_components
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


def test_get_dsd_qube_components_for_csv_standard_shape():
    """
    Test that dsd components from a standard shape dataset are
    correctly returned by the inspector function get_dsd_qube_components_for_csv
    """
    path_to_json_file = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(path_to_json_file)
    data_cube_inspector = get_data_cube_inspector(path_to_json_file)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_state.get_primary_catalog_metadata()
    )
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    result: QubeComponentsResult = data_cube_inspector.get_dsd_qube_components_for_csv(
        csv_url
    )

    assert result is not None

    components = result.qube_components
    assert len(components) == 6

    component = get_dsd_component_by_property_url(
        components, "http://purl.org/linked-data/sdmx/2009/dimension#refPeriod"
    )
    assert_dsd_component_equal(
        component,
        "http://purl.org/linked-data/sdmx/2009/dimension#refPeriod",
        ComponentPropertyType.Dimension,
        "",
        ["Period"],
        [""],
        "energy-trends-uk-total-energy.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(
        components, "http://purl.org/linked-data/sdmx/2009/dimension#refArea"
    )
    assert_dsd_component_equal(
        component,
        "http://purl.org/linked-data/sdmx/2009/dimension#refArea",
        ComponentPropertyType.Dimension,
        "",
        ["Region"],
        [""],
        "energy-trends-uk-total-energy.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(
        components, "http://gss-data.org.uk/def/energy/property/dimension/fuel"
    )
    assert_dsd_component_equal(
        component,
        "http://gss-data.org.uk/def/energy/property/dimension/fuel",
        ComponentPropertyType.Dimension,
        "",
        ["Fuel"],
        [""],
        "energy-trends-uk-total-energy.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(
        components, "http://purl.org/linked-data/cube#measureType"
    )
    assert_dsd_component_equal(
        component,
        "http://purl.org/linked-data/cube#measureType",
        ComponentPropertyType.Dimension,
        "",
        ["Measure Type"],
        [""],
        "energy-trends-uk-total-energy.csv#structure",
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
        ["Unit"],
        [""],
        "energy-trends-uk-total-energy.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(
        components, "energy-trends-uk-total-energy.csv#measure/energy-consumption"
    )
    assert_dsd_component_equal(
        component,
        "energy-trends-uk-total-energy.csv#measure/energy-consumption",
        ComponentPropertyType.Measure,
        "energy-consumption",
        [],
        [],
        "energy-trends-uk-total-energy.csv#structure",
        True,
    )
