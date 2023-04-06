import pytest

from csvcubed.definitions import QB_MEASURE_TYPE_DIMENSION_URI, SDMX_ATTRIBUTE_UNIT_URI
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import (
    CodelistResult,
    CodelistsResult,
    CubeTableIdentifiers,
    QubeComponentsResult,
    UnitResult,
)
from csvcubed.utils.iterables import first
from csvcubed.utils.qb.components import ComponentPropertyType, EndUserColumnType
from tests.helpers.inspectors_cache import get_csvw_rdf_manager, get_data_cube_inspector
from tests.unit.cli.inspect.test_inspectdatasetmanager import get_arguments_qb_dataset
from tests.unit.test_baseunit import get_test_cases_dir
from tests.unit.utils.sparqlhandler.test_sparqlquerymanager import (
    assert_dsd_component_equal,
    get_dsd_component_by_property_url,
)

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


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
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
    )

    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    result: CubeTableIdentifiers = data_cube_inspector.get_cube_identifiers_for_csv(
        csv_url
    )

    assert result is not None
    assert result.csv_url == "qb-id-10004.csv"
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
        data_cube_inspector.csvw_inspector.get_primary_catalog_metadata()
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
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
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
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
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
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
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
    Should return expected code lists and column information.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
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
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
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
        components, QB_MEASURE_TYPE_DIMENSION_URI
    )
    assert_dsd_component_equal(
        component,
        QB_MEASURE_TYPE_DIMENSION_URI,
        ComponentPropertyType.Dimension,
        "",
        [],
        [],
        "qb-id-10003.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(components, SDMX_ATTRIBUTE_UNIT_URI)
    assert_dsd_component_equal(
        component,
        SDMX_ATTRIBUTE_UNIT_URI,
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
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
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
        components, QB_MEASURE_TYPE_DIMENSION_URI
    )
    assert_dsd_component_equal(
        component,
        QB_MEASURE_TYPE_DIMENSION_URI,
        ComponentPropertyType.Dimension,
        "",
        [],
        [],
        "qb-id-10004.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(components, SDMX_ATTRIBUTE_UNIT_URI)
    assert_dsd_component_equal(
        component,
        SDMX_ATTRIBUTE_UNIT_URI,
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
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
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
        components, QB_MEASURE_TYPE_DIMENSION_URI
    )
    assert_dsd_component_equal(
        component,
        QB_MEASURE_TYPE_DIMENSION_URI,
        ComponentPropertyType.Dimension,
        "",
        ["Measure Type"],
        [""],
        "energy-trends-uk-total-energy.csv#structure",
        True,
    )

    component = get_dsd_component_by_property_url(components, SDMX_ATTRIBUTE_UNIT_URI)
    assert_dsd_component_equal(
        component,
        SDMX_ATTRIBUTE_UNIT_URI,
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
        ["Measure Type"],
        ["Value"],
        "energy-trends-uk-total-energy.csv#structure",
        True,
    )


def test_pivoted_column_component_info():
    """This text checks 'get_column_component_info' returns a List of ColumnComponentInfo object in the correct order
    (that was defined in the corresponding CSV file), and contains the correct data in pivoted shape.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-single-unit-component"
        / "multi-measure-pivoted-dataset-units-and-attributes.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)

    (_, _, csv_url) = get_arguments_qb_dataset(data_cube_inspector)

    list_of_columns_definitions = data_cube_inspector.get_column_component_info(csv_url)

    # get the test to check the properties and make sure the types match and the columns definitions match in the
    # correct order

    expected_component_types = [
        "Dimension",
        "Dimension",
        "Observations",
        "Attribute",
        "Observations",
        "Attribute",
        "Units",
    ]

    # this test will compare the two list's values and order
    actual_components_types = [
        item.column_type.value for item in list_of_columns_definitions
    ]
    assert actual_components_types == expected_component_types


def test_standard_column_component_info():
    """This text checks 'get_column_component_info' returns a List of ColumnComponentInfo object in the correct order
    (that was defined in the corresponding CSV file), and contains the correct data, in standard shape.
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)

    (_, _, csv_url) = get_arguments_qb_dataset(data_cube_inspector)

    list_of_columns_definitions = data_cube_inspector.get_column_component_info(csv_url)

    # get the test to check the properties and make sure the types match and the columns definitions match in the
    # correct order

    expected_component_types = [
        "Dimension",
        "Dimension",
        "Dimension",
        "Measures",
        "Units",
        "Observations",
    ]

    # this test will compare the two list's values and order
    actual_components_types = [
        item.column_type.value for item in list_of_columns_definitions
    ]
    assert actual_components_types == expected_component_types


# write a test to scheck if a column is supressed will it get the new type
def test_supressed_column_info():
    """
    This text checks 'get_column_component_info' returns a List of ColumnComponentInfo object in the correct order
    (that was defined in the corresponding CSV file),in this test emphasis on SUpressed columns, and contains
    the correct data, in satndard shape.
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "suppressed-column-cube"
        / "suppressed-data-example.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)

    (_, _, csv_url) = get_arguments_qb_dataset(data_cube_inspector)

    list_of_columns_definitions = data_cube_inspector.get_column_component_info(csv_url)

    # get the test to check the properties and make sure the types match and the columns definitions match in the
    # correct order

    expected_component_types = [
        "Dimension",
        "Observations",
        "Suppressed",
    ]

    # this test will compare the two list's values and order
    actual_components_types = [
        item.column_type.value for item in list_of_columns_definitions
    ]
    assert actual_components_types == expected_component_types


def test_standard_column_component_property_url():
    """This text checks '_get_column_components_and_check_for_cube_shape'
    returns the correct column based of the cube shape and the property_url.
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)

    (_, _, csv_url) = get_arguments_qb_dataset(data_cube_inspector)

    column_components = data_cube_inspector.get_dsd_qube_components_for_csv(csv_url)

    column_definitions = data_cube_inspector.get_column_component_info(csv_url)
    column_definitions = [x.column_definition for x in column_definitions]

    measure_column = first(
        column_definitions,
        lambda c: c.title == "Measure Type",
    )
    observations_column = first(
        column_definitions,
        lambda c: c.title == "Value",
    )

    measure_component = first(
        column_components.qube_components,
        lambda c: c.property_type == "Measure",
    )
    assert measure_column is not None
    assert measure_component is not None
    assert measure_component.real_columns_used_in == [measure_column]
    assert measure_component.used_by_observed_value_columns == [observations_column]


def test_get_columns_for_component_dimension():
    """
    This test check if the function returns a
    list of ColumnDefinition with the correct values(for Dimension).
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    (_, _, csv_url) = get_arguments_qb_dataset(data_cube_inspector)

    delivered_columns = data_cube_inspector.get_columns_of_type(
        csv_url, EndUserColumnType.Dimension
    )

    # The title names has been checked in the csv
    actual_titles = [x.title for x in delivered_columns]
    expected_titles = ["Period", "Region", "Fuel"]

    assert actual_titles == expected_titles


def test_get_columns_for_component_unit():
    """
    This test check if the function returns a
    list of ColumnDefinition with the correct values(for Units).
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    (_, _, csv_url) = get_arguments_qb_dataset(data_cube_inspector)

    delivered_columns = data_cube_inspector.get_columns_of_type(
        csv_url, EndUserColumnType.Units
    )

    # The title names has been checked in the csv
    actual_titles = [x.title for x in delivered_columns]
    expected_titles = ["Unit"]

    assert actual_titles == expected_titles


def test_get_columns_for_component_observation():
    """
    This test check if the function returns a
    list of ColumnDefinition with the correct values(for Observations).
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    (_, _, csv_url) = get_arguments_qb_dataset(data_cube_inspector)

    delivered_columns = data_cube_inspector.get_columns_of_type(
        csv_url, EndUserColumnType.Observations
    )

    # The title names has been checked in the csv
    actual_titles = [x.title for x in delivered_columns]
    expected_titles = ["Value"]

    assert actual_titles == expected_titles


def test_get_columns_for_component_measures():
    """
    This test check if the function returns a
    list of ColumnDefinition with the correct values(for Measures).
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    (_, _, csv_url) = get_arguments_qb_dataset(data_cube_inspector)

    delivered_columns = data_cube_inspector.get_columns_of_type(
        csv_url, EndUserColumnType.Measures
    )

    # The title names has been checked in the csv
    actual_titles = [x.title for x in delivered_columns]
    expected_titles = ["Measure Type"]

    assert actual_titles == expected_titles


def test_get_columns_for_component_attribute():
    """
    This test check if the function returns a
    list of ColumnDefinition with the correct values(for Attribute).
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "single-unit_single-measure"
        / "energy-trends-uk-total-energy.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    (_, _, csv_url) = get_arguments_qb_dataset(data_cube_inspector)

    delivered_columns = data_cube_inspector.get_columns_of_type(
        csv_url, EndUserColumnType.Attribute
    )

    # The title names has been checked in the csv
    actual_titles = [x.title for x in delivered_columns]
    # this csv doens't contain attribute column so the expected return is an epmty list
    expected_titles = []

    assert actual_titles == expected_titles


def test_get_columns_for_component_attribute_pivoted():
    """
    This test check if the function returns a
    list of ColumnDefinition with the correct values.
    (using a different dataset to demonstrate the function
     does return attribut columns as well if there is any)
    """

    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-single-unit-component"
        / "multi-measure-pivoted-dataset-units-and-attributes.csv-metadata.json"
    )

    data_cube_inspector = get_data_cube_inspector(csvw_metadata_json_path)
    (_, _, csv_url) = get_arguments_qb_dataset(data_cube_inspector)

    delivered_columns = data_cube_inspector.get_columns_of_type(
        csv_url, EndUserColumnType.Attribute
    )

    # The title names has been checked in the csv
    actual_titles = [x.title for x in delivered_columns]
    expected_titles = ["Imports Status", "Exports Status"]

    assert actual_titles == expected_titles


def test_get_measure_uris_and_labels_pivoted_multi_measure():
    path_to_json_file = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(path_to_json_file)
    data_cube_inspector = get_data_cube_inspector(path_to_json_file)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
    )
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    result = data_cube_inspector.get_measure_uris_and_labels(csv_url)

    assert len(result) == 2
    assert result["qb-id-10003.csv#measure/some-other-measure"] == "Some Other Measure"
    assert result["qb-id-10003.csv#measure/some-measure"] == "Some Measure"


def test_get_measure_uris_and_labels_standard_multi_measure():
    path_to_json_file = (
        _test_case_base_dir
        / "multi-unit_multi-measure"
        / "new"
        / "alcohol-bulletin.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(path_to_json_file)
    data_cube_inspector = get_data_cube_inspector(path_to_json_file)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
    )
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    result = data_cube_inspector.get_measure_uris_and_labels(csv_url)

    assert len(result) == 9
    assert (
        result["alcohol-bulletin.csv#measure/alcohol-duty-receipts"]
        == "alcohol-duty-receipts"
    )
    assert (
        result["alcohol-bulletin.csv#measure/beer-duty-receipts"]
        == "beer-duty-receipts"
    )
    assert (
        result["alcohol-bulletin.csv#measure/cider-duty-receipts"]
        == "cider-duty-receipts"
    )
    assert result["alcohol-bulletin.csv#measure/clearances"] == "clearances"
    assert (
        result["alcohol-bulletin.csv#measure/clearances-of-alcohol"]
        == "clearances-of-alcohol"
    )
    assert (
        result["alcohol-bulletin.csv#measure/production-volume"] == "production-volume"
    )
    assert (
        result["alcohol-bulletin.csv#measure/production-volume-alcohol"]
        == "production-volume-alcohol"
    )
    assert (
        result["alcohol-bulletin.csv#measure/spirits-duty-receipts"]
        == "spirits-duty-receipts"
    )
    assert (
        result["alcohol-bulletin.csv#measure/wine-duty-receipts"]
        == "wine-duty-receipts"
    )


def test_get_attribute_value_uris_and_labels():
    path_to_json_file = (
        _test_case_base_dir
        / "multi-attribute-resource-values"
        / "multi-attribute.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(path_to_json_file)
    data_cube_inspector = get_data_cube_inspector(path_to_json_file)
    primary_catalog_metadata = (
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
    )
    csv_url = data_cube_inspector.get_cube_identifiers_for_data_set(
        primary_catalog_metadata.dataset_uri
    ).csv_url

    result = data_cube_inspector.get_attribute_value_uris_and_labels(csv_url)

    assert len(result) == 2
    assert result["imports_status"][0].resource_label == "Final"
    assert (
        result["imports_status"][0].resource_uri
        == "multi-attribute.csv#attribute/imports-status/final"
    )
    assert result["imports_status"][1].resource_label == "Provisional"
    assert (
        result["imports_status"][1].resource_uri
        == "multi-attribute.csv#attribute/imports-status/provisional"
    )
    assert result["imports_status"][2].resource_label == "Forecast"
    assert (
        result["imports_status"][2].resource_uri
        == "multi-attribute.csv#attribute/imports-status/forecast"
    )
    assert result["exports_status"][0].resource_label == "Final"
    assert (
        result["exports_status"][0].resource_uri
        == "multi-attribute.csv#attribute/imports-status/final"
    )
    assert result["exports_status"][1].resource_label == "Provisional"
    assert (
        result["exports_status"][1].resource_uri
        == "multi-attribute.csv#attribute/imports-status/provisional"
    )
    assert result["exports_status"][2].resource_label == "Forecast"
    assert (
        result["exports_status"][2].resource_uri
        == "multi-attribute.csv#attribute/imports-status/forecast"
    )
