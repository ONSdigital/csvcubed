import os
from pathlib import Path

import pytest
from pandas.testing import assert_frame_equal

from csvcubed.cli.inspect.metadatainputvalidator import MetadataValidator
from csvcubed.models.csvwtype import CSVWType
from csvcubed.utils.tableschema import CsvwRdfManager
from tests.helpers.inspectors_cache import get_csvw_rdf_manager, get_data_cube_inspector
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_detect_valid_csvw_metadata_datacube_input():
    """
    Should return the correct type and shape for the csv-w metadata input.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    csvw_type = csvw_metadata_rdf_validator.detect_csvw_type()

    assert csvw_type == CSVWType.QbDataSet


def test_detect_valid_csvw_metadata_datacube_relative_path():
    """
    Test that providing relative paths to the `MetadataValidator` results in detection of the correct CSV-W type
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    csvw_metadata_json_path = Path(os.path.relpath(csvw_metadata_json_path, Path(".")))

    assert not csvw_metadata_json_path.is_absolute()

    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    csvw_type = csvw_metadata_rdf_validator.detect_csvw_type()

    assert csvw_type == CSVWType.QbDataSet


def test_detect_valid_csvw_metadata_codelist_input():
    """
    Should return the correct type and shape for the code list csv-w metadata input.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    csvw_type = csvw_metadata_rdf_validator.detect_csvw_type()

    assert csvw_type == CSVWType.CodeList


def test_detect_invalid_csvw_metadata_input():
    """
    Should throw an exception if the csv-w metadata input is not a data cube or code list.
    """

    csvw_metadata_json_path = _test_case_base_dir / "json.table.json"
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph
    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    with pytest.raises(Exception) as exception:
        csvw_metadata_rdf_validator.detect_csvw_type()

    assert (
        str(exception.value)
        == f"The input metadata is invalid as it is not a data cube or a code list."
    )


def test_detect_type_datacube():
    """
    Should return CSVWType.QbDataSet is the input csv-w is a db:Dataset.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    csvw_type = csvw_metadata_rdf_validator.detect_csvw_type()

    assert csvw_type == CSVWType.QbDataSet


def test_detect_type_codelist():
    """
    Should return CSVWType.CodeList is the input csv-w is a skos:ConceptScheme.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    csvw_rdf_manager = get_csvw_rdf_manager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    csvw_type = csvw_metadata_rdf_validator.detect_csvw_type()

    assert csvw_type == CSVWType.CodeList
