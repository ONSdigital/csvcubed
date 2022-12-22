from difflib import ndiff
from pathlib import Path

import pandas as pd
from behave import *
from csvcubeddevtools.behaviour.file import get_context_temp_dir_path
from pandas.util.testing import assert_frame_equal

from csvcubed.cli.inspect.metadatainputvalidator import MetadataValidator
from csvcubed.cli.inspect.metadataprinter import MetadataPrinter
from csvcubed.models.csvwtype import CSVWType
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.inspectdataframeresults import (
    DatasetObservationsByMeasureUnitInfoResult,
    DatasetObservationsInfoResult,
)
from csvcubed.models.sparqlresults import (
    CatalogMetadataResult,
    CodelistsResult,
    QubeComponentsResult,
)
from csvcubed.utils.iterables import first
from csvcubed.utils.qb.components import ComponentPropertyType
from csvcubed.utils.sparql_handler.code_list_state import CodeListState
from csvcubed.utils.sparql_handler.data_cube_state import DataCubeState
from csvcubed.utils.sparql_handler.sparqlquerymanager import select_is_pivoted_shape_for_measures_in_data_set
from csvcubed.utils.sparql_handler.sparqlquerymanager import (
    select_is_pivoted_shape_for_measures_in_data_set,
)
from csvcubed.utils.tableschema import CsvwRdfManager
from tests.unit.cli.inspect.test_inspectdatasetmanager import (
    expected_dataframe_pivoted_single_measure,
    expected_dataframe_pivoted_multi_measure,
)
from tests.unit.utils.sparqlhandler.test_sparqlquerymanager import (
    assert_dsd_component_equal,
    get_dsd_component_by_property_url,
)


def _unformat_multiline_string(string: str) -> str:
    """
    Removes characters that related to formatting (e.g. tabs, newlines, etc.). This allows assert equal to be not impacted by the formating of ground-truth and function-returned strings.

    :return: `str` - unformated string
    """
    return "".join(s for s in string if ord(s) > 32 and ord(s) < 126)


@When('the Metadata file path is detected and validated "{csvw_metadata_file}"')
def step_impl(context, csvw_metadata_file: str):
    context.csvw_metadata_json_path = (
        get_context_temp_dir_path(context) / csvw_metadata_file
    )
    path = Path(context.csvw_metadata_json_path)
    assert path.exists() is True


@When('the csv file path is detected and validated "{csv_file}"')
def step_impl(context, csv_file: str):
    context.csv_file_path = get_context_temp_dir_path(context) / csv_file
    path = Path(context.csv_file_path)
    assert path.exists() is True


@When("the Metadata File json-ld is loaded to a rdf graph")
def step_impl(context):
    csvw_rdf_manager = CsvwRdfManager(context.csvw_metadata_json_path)
    context.csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph
    assert context.csvw_metadata_rdf_graph is not None


@When("the Metadata File is validated")
def step_impl(context):

    csvw_metadata_rdf_validator = MetadataValidator(
        context.csvw_metadata_rdf_graph, context.csvw_metadata_json_path
    )
    is_pivoted_measures = select_is_pivoted_shape_for_measures_in_data_set(
        context.csvw_metadata_rdf_graph
    )
    (
        context.csvw_type,
        context.cube_shape,
    ) = csvw_metadata_rdf_validator.detect_type_and_shape(is_pivoted_measures)

    assert context.csvw_type is not None


@When("the Printables for data cube are generated")
def step_impl(context):
    data_cube_state = DataCubeState(context.csvw_metadata_rdf_graph, context.cube_shape, context.csvw_metadata_json_path)
    metadata_printer = MetadataPrinter(
        data_cube_state,
        None,
        context.csvw_type,
        context.cube_shape,
        context.csvw_metadata_rdf_graph,
        context.csvw_metadata_json_path,
    )
    # TODO: Remove below once all the tests are updated to not match strings
    context.type_printable = metadata_printer.type_info_printable
    context.catalog_metadata_printable = metadata_printer.catalog_metadata_printable
    context.dsd_info_printable = metadata_printer.dsd_info_printable
    context.codelist_info_printable = metadata_printer.codelist_info_printable
    context.dataset_observations_info_printable = (
        metadata_printer.dataset_observations_info_printable
    )
    context.dataset_val_counts_by_measure_unit_info_printable = (
        metadata_printer.dataset_val_counts_by_measure_unit_info_printable
    )

    assert (
        context.type_printable
        and context.catalog_metadata_printable
        and context.dsd_info_printable
        and context.codelist_info_printable
        and context.dataset_observations_info_printable
        and context.dataset_val_counts_by_measure_unit_info_printable
    )
    # TODO: Remove above once all the tests are updated to not match strings

    context.result_type_info = metadata_printer.csvw_type
    context.result_catalog_metadata = metadata_printer.result_catalog_metadata
    context.result_qube_components = metadata_printer.result_qube_components
    context.result_dataset_observations_info = (
        metadata_printer.result_dataset_observations_info
    )
    context.result_code_lists = metadata_printer.result_code_lists
    context.result_dataset_observations_info = (
        metadata_printer.result_dataset_observations_info
    )
    context.result_dataset_value_counts = metadata_printer.result_dataset_value_counts


@When("the Printables for code list are generated")
def step_impl(context):
    code_list_state = CodeListState(context.csvw_metadata_rdf_graph)
    metadata_printer = MetadataPrinter(
        None,
        code_list_state,
        context.csvw_type,
        None,
        context.csvw_metadata_rdf_graph,
        context.csvw_metadata_json_path,
    )
    context.type_printable = metadata_printer.type_info_printable
    context.catalog_metadata_printable = metadata_printer.catalog_metadata_printable
    context.dataset_observations_info_printable = (
        metadata_printer.dataset_observations_info_printable
    )
    context.codelist_hierachy_info_printable = (
        metadata_printer.codelist_hierachy_info_printable
    )

    assert (
        context.type_printable
        and context.catalog_metadata_printable
        and context.dataset_observations_info_printable
        and context.codelist_hierachy_info_printable
    )


@Then('the Type Printable should be "{type_printable}"')
def step_impl(context, type_printable: str):
    assert type_printable == context.type_printable


@Then("the Catalog Metadata Printable should be")
def step_impl(context):
    assert _unformat_multiline_string(
        context.catalog_metadata_printable
    ) == _unformat_multiline_string(context.text.strip())


@Then("the Data Structure Definition Printable should be")
def step_impl(context):
    assert _unformat_multiline_string(
        context.dsd_info_printable
    ) == _unformat_multiline_string(context.text.strip())


@Then("the Code List Printable should be")
def step_impl(context):
    actual_value = _unformat_multiline_string(context.codelist_info_printable)
    expected_value = _unformat_multiline_string(context.text.strip())
    assert expected_value == actual_value, "\n".join(
        ndiff(
            expected_value.splitlines(keepends=True),
            actual_value.splitlines(keepends=True),
        )
    )


@Then("the Dataset Information Printable should be")
def step_impl(context):
    assert _unformat_multiline_string(
        context.dataset_observations_info_printable
    ) == _unformat_multiline_string(context.text.strip())


@Then("the Dataset Value Counts Printable should be")
def step_impl(context):
    assert _unformat_multiline_string(
        context.dataset_val_counts_by_measure_unit_info_printable
    ) == _unformat_multiline_string(context.text.strip())


@Then("the Concepts Information Printable should be")
def step_impl(context):
    assert _unformat_multiline_string(
        context.codelist_hierachy_info_printable
    ) == _unformat_multiline_string(context.text.strip())


@Given('a none existing test-case file "{csvw_metadata_file}"')
def step_impl(context, csvw_metadata_file: str):
    context.csvw_metadata_file = csvw_metadata_file


@Then('the file not found error is displayed "{error_message}"')
def step_impl(context, error_message: str):
    try:
        _ = get_context_temp_dir_path(context) / context.csvw_metadata_file
    except Exception as ex:
        assert ex is not None
        assert ex.message == f"{error_message} {context.csvw_metadata_file}"


@Then("the Type printable is validated for single-measure pivoted data set")
def step_impl(context):
    result_type_info: CSVWType = context.result_type_info
    assert result_type_info is not None
    assert result_type_info == CSVWType.QbDataSet


@Then(
    "the Catalog Metadata printable is validated for single-measure pivoted data set with identifier qb-id-10004"
)
def step_impl(context):
    result_catalog_metadata: CatalogMetadataResult = context.result_catalog_metadata
    assert result_catalog_metadata is not None
    assert result_catalog_metadata.title == "Pivoted Shape Cube"
    assert result_catalog_metadata.label == "Pivoted Shape Cube"
    assert result_catalog_metadata.issued == "2022-10-28T13:35:50.699296"
    assert result_catalog_metadata.modified == "2022-10-28T13:35:50.699296"
    assert result_catalog_metadata.license == "None"
    assert result_catalog_metadata.creator == "None"
    assert result_catalog_metadata.publisher == "None"
    assert (
        len(result_catalog_metadata.landing_pages) == 1
        and result_catalog_metadata.landing_pages[0] == ""
    )
    assert (
        len(result_catalog_metadata.themes) == 1
        and result_catalog_metadata.themes[0] == ""
    )
    assert (
        len(result_catalog_metadata.keywords) == 1
        and result_catalog_metadata.keywords[0] == ""
    )
    assert result_catalog_metadata.contact_point == "None"
    assert result_catalog_metadata.identifier == "qb-id-10004"
    assert result_catalog_metadata.comment == "None"
    assert result_catalog_metadata.description == "None"


@Then(
    "the Data Structure Definition printable is validated for single-measure pivoted data set"
)
def step_impl(context):
    result_qube_components: QubeComponentsResult = context.result_qube_components
    assert result_qube_components is not None

    components = result_qube_components.qube_components
    assert len(components) == 5

    component = get_dsd_component_by_property_url(
        components, "qb-id-10004.csv#dimension/some-dimension"
    )
    assert_dsd_component_equal(component, "qb-id-10004.csv#dimension/some-dimension", ComponentPropertyType.Dimension,
                               "Some Dimension", "Some Dimension", "Some Obs Val", "qb-id-10004.csv#structure", True)

    component = get_dsd_component_by_property_url(
        components, "qb-id-10004.csv#attribute/some-attribute"
    )
    assert_dsd_component_equal(component, "qb-id-10004.csv#attribute/some-attribute", ComponentPropertyType.Attribute,
                               "Some Attribute", "Some Attribute", "Some Obs Val", "qb-id-10004.csv#structure", False)

    component = get_dsd_component_by_property_url(
        components, "http://purl.org/linked-data/cube#measureType"
    )
    assert_dsd_component_equal(component, "http://purl.org/linked-data/cube#measureType",
                               ComponentPropertyType.Dimension, "", "", "", "qb-id-10004.csv#structure", True)

    component = get_dsd_component_by_property_url(
        components, "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
    )
    assert_dsd_component_equal(component, "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure",
                               ComponentPropertyType.Attribute, "", "", "Some Obs Val", "qb-id-10004.csv#structure",
                               True)

    component = get_dsd_component_by_property_url(
        components, "qb-id-10004.csv#measure/some-measure"
    )
    assert_dsd_component_equal(component, "qb-id-10004.csv#measure/some-measure", ComponentPropertyType.Measure,
                               "Some Measure", "Some Obs Val", "Some Obs Val", "qb-id-10004.csv#structure", True)


@Then("the Code List printable is validated for single-measure pivoted data set")
def step_impl(context):
    result_code_lists: CodelistsResult = context.result_code_lists
    assert result_code_lists is not None

    assert len(result_code_lists.codelists) == 1
    assert (
        first(result_code_lists.codelists, lambda c: c.cols_used_in == "Some Dimension")
        is not None
    )


@Then(
    "the Data Set Information printable is validated for single-measure pivoted data set"
)
def step_impl(context):
    result_dataset_observations_info: DatasetObservationsInfoResult = (
        context.result_dataset_observations_info
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


@Then("the Value Counts printable is validated for single-measure pivoted data set")
def step_impl(context):
    result_dataset_value_counts: DatasetObservationsByMeasureUnitInfoResult = (
        context.result_dataset_value_counts
    )
    assert result_dataset_value_counts is not None

    expected_df = pd.DataFrame(
        [
            {
                "Measure": "Some Measure",
                "Unit": "qb-id-10004.csv#unit/some-unit",
                "Count": 3,
            }
        ]
    )
    assert result_dataset_value_counts.by_measure_and_unit_val_counts_df.empty == False
    assert_frame_equal(
        result_dataset_value_counts.by_measure_and_unit_val_counts_df, expected_df
    )


@Then("the Type printable is validated for multi-measure pivoted data set")
def step_impl(context):
    result_type_info: CSVWType = context.result_type_info
    assert result_type_info is not None
    assert result_type_info == CSVWType.QbDataSet


@Then(
    "the Catalog Metadata printable is validated for multi-measure pivoted data set with identifier qb-id-10003"
)
def step_impl(context):
    result_catalog_metadata: CatalogMetadataResult = context.result_catalog_metadata
    assert result_catalog_metadata is not None
    assert result_catalog_metadata.title == "Pivoted Shape Cube"
    assert result_catalog_metadata.label == "Pivoted Shape Cube"
    assert result_catalog_metadata.issued == "2022-11-24T11:45:07.291860"
    assert result_catalog_metadata.modified == "2022-11-24T11:45:07.291860"
    assert result_catalog_metadata.license == "None"
    assert result_catalog_metadata.creator == "None"
    assert result_catalog_metadata.publisher == "None"
    assert (
        len(result_catalog_metadata.landing_pages) == 1
        and result_catalog_metadata.landing_pages[0] == ""
    )
    assert (
        len(result_catalog_metadata.themes) == 1
        and result_catalog_metadata.themes[0] == ""
    )
    assert (
        len(result_catalog_metadata.keywords) == 1
        and result_catalog_metadata.keywords[0] == ""
    )
    assert result_catalog_metadata.contact_point == "None"
    assert result_catalog_metadata.identifier == "qb-id-10003"
    assert result_catalog_metadata.comment == "None"
    assert result_catalog_metadata.description == "None"


@Then(
    "the Data Structure Definition printable is validated for multi-measure pivoted data set"
)
def step_impl(context):
    result_qube_components: QubeComponentsResult = context.result_qube_components
    assert result_qube_components is not None

    components = result_qube_components.qube_components
    assert len(components) == 7

    component = get_dsd_component_by_property_url(
        components, "qb-id-10003.csv#dimension/some-dimension"
    )
    assert_dsd_component_equal(component, "qb-id-10003.csv#dimension/some-dimension", ComponentPropertyType.Dimension,
                               "Some Dimension", "Some Dimension", "Some Obs Val, Some Other Obs Val",
                               "qb-id-10003.csv#structure", True)

    component = get_dsd_component_by_property_url(
        components, "qb-id-10003.csv#attribute/some-attribute"
    )
    assert_dsd_component_equal(component, "qb-id-10003.csv#attribute/some-attribute", ComponentPropertyType.Attribute,
                               "Some Attribute", "Some Attribute", "Some Obs Val", "qb-id-10003.csv#structure", False)

    component = get_dsd_component_by_property_url(
        components, "http://purl.org/linked-data/cube#measureType"
    )
    assert_dsd_component_equal(component, "http://purl.org/linked-data/cube#measureType",
                               ComponentPropertyType.Dimension, "", "", "", "qb-id-10003.csv#structure", True)

    component = get_dsd_component_by_property_url(
        components, "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
    )
    assert_dsd_component_equal(component, "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure",
                               ComponentPropertyType.Attribute, "", "Some Unit", "Some Other Obs Val, Some Obs Val",
                               "qb-id-10003.csv#structure", True)

    component = get_dsd_component_by_property_url(
        components, "qb-id-10003.csv#measure/some-measure"
    )
    assert_dsd_component_equal(component, "qb-id-10003.csv#measure/some-measure", ComponentPropertyType.Measure,
                               "Some Measure", "Some Obs Val", "Some Obs Val", "qb-id-10003.csv#structure", True)

    component = get_dsd_component_by_property_url(
        components, "qb-id-10003.csv#measure/some-other-measure"
    )
    assert_dsd_component_equal(component, "qb-id-10003.csv#measure/some-other-measure", ComponentPropertyType.Measure,
                               "Some Other Measure", "Some Other Obs Val", "Some Other Obs Val",
                               "qb-id-10003.csv#structure", True)


@Then("the Code List printable is validated for multi-measure pivoted data set")
def step_impl(context):
    result_code_lists: CodelistsResult = context.result_code_lists
    assert result_code_lists is not None

    assert len(result_code_lists.codelists) == 1
    assert (
        first(result_code_lists.codelists, lambda c: c.cols_used_in == "Some Dimension")
        is not None
    )


@Then(
    "the Data Set Information printable is validated for multi-measure pivoted data set"
)
def step_impl(context):
    result_dataset_observations_info: DatasetObservationsInfoResult = (
        context.result_dataset_observations_info
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


@Then("the Value Counts printable is validated for multi-measure pivoted data set")
def step_impl(context):
    result_dataset_value_counts: DatasetObservationsByMeasureUnitInfoResult = (
        context.result_dataset_value_counts
    )
    assert result_dataset_value_counts is not None
    
    expected_df = pd.DataFrame(
        [
            {
                "Measure": "Some Measure",
                "Unit": "qb-id-10003.csv#unit/some-unit",
                "Count": 3,
            },
                {
                "Measure": "Some Other Measure",
                "Unit": "qb-id-10003.csv#unit/percent",
                "Count": 3,
            }
        ]
    )
    assert result_dataset_value_counts.by_measure_and_unit_val_counts_df.empty == False
    assert_frame_equal(
        result_dataset_value_counts.by_measure_and_unit_val_counts_df, expected_df
    )
