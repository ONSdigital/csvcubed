from pathlib import Path

from behave import *

from csvcubeddevtools.behaviour.file import get_context_temp_dir_path
from csvcubed.cli.inspect.metadatainputvalidator import MetadataValidator
from csvcubed.cli.inspect.metadataprinter import MetadataPrinter
from csvcubed.cli.inspect.metadataprocessor import MetadataProcessor


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
    metadata_processor = MetadataProcessor(context.csvw_metadata_json_path)
    context.csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()
    assert context.csvw_metadata_rdf_graph is not None


@When("the Metadata File is validated")
def step_impl(context):
    csvw_metadata_rdf_validator = MetadataValidator(context.csvw_metadata_rdf_graph)
    (
        context.valid_csvw_metadata,
        context.csvw_type,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    assert context.valid_csvw_metadata is True


@When("the Printables for data cube are generated")
def step_impl(context):
    metadata_printer = MetadataPrinter(
        context.csvw_type,
        context.csvw_metadata_rdf_graph,
        context.csvw_metadata_json_path,
    )
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


@When("the Printables for code list are generated")
def step_impl(context):
    metadata_printer = MetadataPrinter(
        context.csvw_type,
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
    ) == _unformat_multiline_string(context.text)


@Then("the Data Structure Definition Printable should be")
def step_impl(context):
    assert _unformat_multiline_string(
        context.dsd_info_printable
    ) == _unformat_multiline_string(context.text)


@Then("the Code List Printable should be")
def step_impl(context):
    assert _unformat_multiline_string(
        context.codelist_info_printable
    ) == _unformat_multiline_string(context.text)


@Then("the Dataset Information Printable should be")
def step_impl(context):
    assert _unformat_multiline_string(
        context.dataset_observations_info_printable
    ) == _unformat_multiline_string(context.text)


@Then("the Dataset Value Counts Printable should be")
def step_impl(context):
    assert _unformat_multiline_string(
        context.dataset_val_counts_by_measure_unit_info_printable
    ) == _unformat_multiline_string(context.text)


@Then("the Concepts Information Printable should be")
def step_impl(context):
    assert _unformat_multiline_string(
        context.codelist_hierachy_info_printable
    ) == _unformat_multiline_string(context.text)


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
