from pathlib import Path

import pytest
from rdflib import ConjunctiveGraph

from csvcubed.models.csvwtype import CSVWType
from csvcubed.utils.sparql_handler.csvw_inspector import CsvWInspector
from csvcubed.utils.sparql_handler.sparql import path_to_file_uri_for_rdflib
from tests.helpers.inspectors_cache import get_csvw_rdf_manager
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_get_primary_catalog_metadata():
    """
    Tests that primary catalog metadata can correctly be retrieved from an input
    csvw metadata json file's CsvWRdfManager object, by accessing its csvw_inspector and
    running the function.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    primary_graph_identifier = path_to_file_uri_for_rdflib(csvw_metadata_json_path)

    test_catalog_metadata_result = (
        csvw_rdf_manager.csvw_inspector.get_primary_catalog_metadata()
    )

    assert test_catalog_metadata_result.graph_uri == primary_graph_identifier


def test_get_primary_catalog_metadata_key_error():
    """
    Test to ensure that when primary catalog metadata cannot be returned for a
    particular graph, the API function returns a KeyError instead.
    """
    rdf_graph = ConjunctiveGraph()

    csvw_inspector = CsvWInspector(rdf_graph, Path("does-not-exist.csv-metadata.json"))

    with pytest.raises(KeyError) as exception:
        assert csvw_inspector.get_primary_catalog_metadata()

    assert (
        f"Could not find catalog metadata in primary graph '{csvw_inspector.primary_graph_uri}'."
        in str(exception.value)
    )


def test_detect_csvw_type_qb_dataset():
    """
    Tests the detection of the csvw_type of an input metadata json file that has a CsvWRdfManager
    object created from it, in this case to correctly detect a QbDataset csvw type from its csvw_inspector.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "qb-id-10004.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)

    csvw_type = csvw_rdf_manager.csvw_inspector.csvw_type
    assert csvw_type == CSVWType.QbDataSet


def test_csvw_type_key_error():
    """
    Test to ensure that when a conjunctive graph that is not recognised by the
    csvw_type() function as a code list or a qb data set returns a type error.
    """

    rdf_graph = ConjunctiveGraph()

    csvw_inspector = CsvWInspector(rdf_graph, Path("does-not-exist.csv-metadata.json"))

    with pytest.raises(TypeError) as exception:
        assert csvw_inspector.csvw_type()

    assert (
        "The input metadata is invalid as it is not a data cube or a code list."
        in str(exception.value)
    )


def test_detect_csvw_type_code_list():
    """
    Tests the detection of the csvw_type of an input metadata json file that has a CsvWRdfManager
    object created from it, in this case to correctly detect a CodeList csvw type from its csvw_inspector.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "some-dimension.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)

    csvw_type = csvw_rdf_manager.csvw_inspector.csvw_type
    assert csvw_type == CSVWType.CodeList


def test_get_table_info_for_csv_url():
    """
    Ensures that the correct table schema properties are returned for the given code list.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-single-measure-dataset"
        / "some-dimension.csv-metadata.json"
    )
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)

    csvw_inspector: CsvWInspector = CsvWInspector(
        csvw_rdf_manager.rdf_graph, csvw_metadata_json_path
    )

    result = csvw_inspector.get_table_info_for_csv_url("some-dimension.csv")

    assert result.about_url == "some-dimension.csv#{+uri_identifier}"
    assert result.csv_url == "some-dimension.csv"
    assert result.primary_key_col_names == ["uri_identifier"]


def test_get_table_info_multiple_tables():
    """
    Tests retrieval of all tables from a data cube that contains multiple tables.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)

    csvw_inspector: CsvWInspector = CsvWInspector(
        csvw_rdf_manager.rdf_graph, csvw_metadata_json_path
    )

    result = csvw_inspector._table_schema_properties

    assert len(result) == 4

    assert (
        result["alcohol-bulletin.csv"].about_url
        == "alcohol-bulletin.csv#obs/{+period}/{+alcohol_type}/{+alcohol_sub_type}/{+alcohol_content}/{+clearance_origin}/{+measure_type}"
    )
    assert result["alcohol-content.csv"].about_url == "alcohol-content.csv#{+notation}"
    assert (
        result["alcohol-sub-type.csv"].about_url == "alcohol-sub-type.csv#{+notation}"
    )
    assert (
        result["clearance-origin.csv"].about_url == "clearance-origin.csv#{+notation}"
    )

    assert set(result["alcohol-bulletin.csv"].primary_key_col_names) == {
        "alcohol_content",
        "alcohol_sub_type",
        "alcohol_type",
        "clearance_origin",
        "measure_type",
        "period",
    }
    assert result["alcohol-content.csv"].primary_key_col_names == ["notation"]
    assert result["clearance-origin.csv"].primary_key_col_names == ["notation"]
    assert result["alcohol-sub-type.csv"].primary_key_col_names == ["notation"]
