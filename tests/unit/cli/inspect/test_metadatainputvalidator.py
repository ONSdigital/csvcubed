import os
from pathlib import Path

import pytest

from csvcubed.cli.inspect.metadatainputvalidator import CSVWType, MetadataValidator
from csvcubed.utils.sparql_handler.sparqlmanager import (
    CubeShape,
    select_is_pivoted_shape_for_measures_in_data_set,
)
from csvcubed.utils.tableschema import CsvwRdfManager
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


def test_detect_valid_csvw_metadata_datacube_input():
    """
    Should return the correct type and shape for the csv-w metadata input.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    is_pivoted_measures = select_is_pivoted_shape_for_measures_in_data_set(
        csvw_metadata_rdf_graph
    )
    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    (
        type,
        shape,
    ) = csvw_metadata_rdf_validator.detect_type_and_shape(is_pivoted_measures)

    assert type == CSVWType.QbDataSet
    assert shape == CubeShape.Standard


def test_detect_valid_csvw_metadata_datacube_relative_path():
    """
    Test that providing relative paths to the `MetadataValidator` results in detection of the correct CSV-W type
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    csvw_metadata_json_path = Path(os.path.relpath(csvw_metadata_json_path, Path(".")))

    assert not csvw_metadata_json_path.is_absolute()

    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    is_pivoted_measures = select_is_pivoted_shape_for_measures_in_data_set(
        csvw_metadata_rdf_graph
    )
    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    (
        type,
        shape,
    ) = csvw_metadata_rdf_validator.detect_type_and_shape(is_pivoted_measures)

    assert type == CSVWType.QbDataSet
    assert shape == CubeShape.Standard

def test_detect_valid_csvw_metadata_codelist_input():
    """
    Should return the correct type and shape for the code list csv-w metadata input.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    is_pivoted_measures = select_is_pivoted_shape_for_measures_in_data_set(
        csvw_metadata_rdf_graph
    )
    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    (
        type,
        shape,
    ) = csvw_metadata_rdf_validator.detect_type_and_shape(is_pivoted_measures)

    assert type == CSVWType.CodeList
    assert shape is None


def test_detect_invalid_csvw_metadata_input():
    """
    Should throw an exception if the csv-w metadata input is not a data cube or code list.
    """

    csvw_metadata_json_path = _test_case_base_dir / "json.table.json"
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path,
    )

    with pytest.raises(Exception) as exception:
        csvw_metadata_rdf_validator._detect_type()
    assert str(exception.value) == f"The input metadata is invalid as it is not a data cube or a code list."


def test_detect_type_datacube():
    """
    Should return CSVWType.QbDataSet is the input csv-w is a db:Dataset.
    """
    csvw_metadata_json_path = _test_case_base_dir / "datacube.csv-metadata.json"
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    is_pivoted_measures = select_is_pivoted_shape_for_measures_in_data_set(
        csvw_metadata_rdf_graph
    )
    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    (csvw_type, _) = csvw_metadata_rdf_validator.detect_type_and_shape(is_pivoted_measures)

    assert csvw_type == CSVWType.QbDataSet


def test_detect_type_codelist():
    """
    Should return CSVWType.CodeList is the input csv-w is a skos:ConceptScheme.
    """
    csvw_metadata_json_path = _test_case_base_dir / "codelist.csv-metadata.json"
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph

    is_pivoted_measures = select_is_pivoted_shape_for_measures_in_data_set(
        csvw_metadata_rdf_graph
    )
    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    (csvw_type, _) = csvw_metadata_rdf_validator.detect_type_and_shape(is_pivoted_measures)

    assert csvw_type == CSVWType.CodeList

def test_detect_csvw_shape_pivoted():
    """
    Ensures that the shape of the cube represented by the input metadata is correctly returned as Pivoted.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-multi-measure-dataset"
        / "qb-id-10003.csv-metadata.json"
    )
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph
    is_pivoted_shape_measures = select_is_pivoted_shape_for_measures_in_data_set(
        csvw_metadata_rdf_graph
    )

    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    (_, cube_shape) = csvw_metadata_rdf_validator.detect_type_and_shape(is_pivoted_shape_measures)

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
    csvw_rdf_manager = CsvwRdfManager(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = csvw_rdf_manager.rdf_graph
    is_pivoted_shape_measures = select_is_pivoted_shape_for_measures_in_data_set(
        csvw_metadata_rdf_graph
    )

    csvw_metadata_rdf_validator = MetadataValidator(
        csvw_metadata_rdf_graph, csvw_metadata_json_path
    )

    (_, cube_shape) = csvw_metadata_rdf_validator.detect_type_and_shape(is_pivoted_shape_measures)

    assert cube_shape == CubeShape.Standard
