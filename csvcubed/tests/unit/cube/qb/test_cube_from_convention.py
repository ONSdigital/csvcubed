import os
from pathlib import Path

import pytest
from csvcubed.cli.build import build as cli_build
from csvcubed.readers.configdeserialiser import *

from tests.unit.test_baseunit import get_test_cases_dir

PROJECT_ROOT = Path(Path(__file__).parent, "..", "..", "..", "..").resolve()
TEST_CASE_DIR = Path(get_test_cases_dir().absolute(), 'config')
SCHEMA_PATH_FILE = Path(PROJECT_ROOT, "csvcubed", "schema", "cube-config-schema.json")


# def test_schema_loads_from_file():
#     # schema_path = os.path.realpath(os.path.join(PROJECT_ROOT, "csvcubed", "schema", "dataset-schema-1.1.0.json"))
#     print(f"schema file path: {SCHEMA_PATH_FILE}")
#     schema = _load_resource(SCHEMA_PATH_FILE)
#     assert isinstance(schema, dict)
#
#
# def test_schema_loads_from_uri():
#     print(f"schema uri: {SCHEMA_PATH_URI}")
#     schema = _load_resource(SCHEMA_PATH_URI)
#     assert isinstance(schema, dict)
#
#
# def test_schema_validation_mininal():
#     json_path = os.path.join(TEST_CASE_DIR, "config-test-1.json")
#     print(json_path)
#
#     if os.path.exists(json_path):
#         with open(json_path, "r") as fp:
#             config_json = json.load(fp)
#         print(type(config_json), config_json)
#         errors = validate_dict_against_schema_url(config_json, SCHEMA_PATH_FILE)
#         print(errors, sep='\n')
#
# def test_build_1():
#     """No Args"""
#     try:
#         with pytest.raises(ValueError) as exc_info:
#             build()
#         assert exc_info.type is ValueError
#         assert exc_info.value.args == "build() missing 1 required positional arguments: 'csv_path'"
#
#     except Exception as err:
#         print(err)

# def test_build_2():
#     """
#     Incorrect types for args
#     TODO - Implement strict type hint checking - https://stackoverflow.com/questions/32844556/python-3-5-type-hints-can-i-check-if-function-arguments-match-type-hints
#     """
#     with pytest.raises(ValueError) as exc_info:
#         build("should_be_path", "should_be_path", "should_be_path",)
#     assert exc_info.type is TypeError
#     assert exc_info.value.args == ""

def test_01_build_convention_ok():
    """
    Valid Cube from Data using Convention (no config json)
    """
    test_data_path = Path(os.path.join(TEST_CASE_DIR, 'cube_data_convention_ok.csv')).resolve()
    test_json_path = None
    print(f"test_case_data: {test_data_path}")
    cube, validation_errors = cli_build(csv_path=test_data_path)
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, List)
    assert isinstance(cube.columns, list)
    for column in cube.columns:
        assert isinstance(column, QbColumn)

    col_dim_0 = cube.columns[0]
    assert isinstance(col_dim_0.structural_definition, NewQbDimension)
    assert isinstance(col_dim_0.structural_definition.code_list, NewQbCodeList)
    assert isinstance(col_dim_0.structural_definition.code_list.metadata, CatalogMetadata)
    assert isinstance(col_dim_0.structural_definition.code_list.concepts, list)
    assert isinstance(col_dim_0.structural_definition.code_list.concepts[0], NewQbConcept)

    col_dim_1 = cube.columns[1]
    assert isinstance(col_dim_1.structural_definition, NewQbDimension)
    assert isinstance(col_dim_1.structural_definition.code_list.metadata, CatalogMetadata)
    assert isinstance(col_dim_1.structural_definition.code_list.concepts, list)
    assert isinstance(col_dim_1.structural_definition.code_list.concepts[0], NewQbConcept)

    col_observation = cube.columns[2]
    assert isinstance(col_observation.structural_definition, QbMultiMeasureObservationValue)
    assert col_observation.structural_definition.unit is None
    assert col_observation.structural_definition.data_type == 'decimal'

    col_measure = cube.columns[3]
    assert isinstance(col_measure.structural_definition, QbMultiMeasureDimension)
    assert isinstance(col_measure.structural_definition.measures, list)
    assert isinstance(col_measure.structural_definition.measures[0], NewQbMeasure)

    col_unit = cube.columns[4]
    assert isinstance(col_unit.structural_definition, QbMultiUnits)
    assert isinstance(col_unit.structural_definition.units, list)
    assert isinstance(col_unit.structural_definition.units[0], NewQbUnit)

    col_attribute = cube.columns[5]
    assert isinstance(col_attribute.structural_definition, NewQbDimension)
    assert isinstance(col_attribute.structural_definition.code_list, NewQbCodeList)
    assert isinstance(col_attribute.structural_definition.code_list.concepts, list)
    assert isinstance(
        col_attribute.structural_definition.code_list.concepts[0], NewQbConcept)


if __name__ == "__main__":
    pytest.main()
