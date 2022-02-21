import os
from pathlib import Path

import pytest
from csvcubed.readers.configdeserialiser import *

from tests.unit.test_baseunit import get_test_cases_dir

PROJECT_ROOT = Path(Path(__file__).parent, "..", "..", "..", "..").resolve()
TEST_CASE_DIR = Path(get_test_cases_dir().absolute(), 'config')
TEST_CASE_DIR = os.path.join(PROJECT_ROOT, "tests", "test-cases", "config")
SCHEMA_PATH_FILE = Path(PROJECT_ROOT, "csvcubed", "schema", "cube-config-schema.json")


def test_01_build_config_ok():
    """
    Valid Cube from Data using Convention (no config json)
    """
    test_data_path = Path(os.path.join(TEST_CASE_DIR, 'cube_data_config_ok.csv')).resolve()
    test_json_path = Path(os.path.join(TEST_CASE_DIR, 'cube_data_config_ok.json')).resolve()
    print(f"test_case_data: {test_data_path}")
    cube, validation_errors = build(csv_path=test_data_path, config_path=test_json_path)
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

    col_dim_2 = cube.columns[2]
    assert isinstance(col_dim_2.structural_definition, NewQbDimension)
    assert isinstance(col_dim_2.structural_definition.code_list.metadata, CatalogMetadata)
    assert isinstance(col_dim_2.structural_definition.code_list.concepts, list)
    assert isinstance(col_dim_2.structural_definition.code_list.concepts[0], NewQbConcept)

    col_attr_1 = cube.columns[3]
    assert isinstance(col_attr_1.structural_definition, NewQbAttribute)
    assert isinstance(col_attr_1.structural_definition.new_attribute_values, list)
    assert isinstance(col_attr_1.structural_definition.new_attribute_values[0], NewQbAttributeValue)

    col_observation = cube.columns[4]
    assert isinstance(col_observation.structural_definition, QbMultiMeasureObservationValue)
    assert col_observation.structural_definition.unit is None
    assert col_observation.structural_definition.data_type == 'decimal'

    col_measure = cube.columns[5]
    assert isinstance(col_measure.structural_definition, QbMultiMeasureDimension)
    assert isinstance(col_measure.structural_definition.measures, list)
    assert isinstance(col_measure.structural_definition.measures[0], NewQbMeasure)

    col_unit = cube.columns[6]
    assert isinstance(col_unit.structural_definition, QbMultiUnits)
    assert isinstance(col_unit.structural_definition.units, list)
    assert isinstance(col_unit.structural_definition.units[0], NewQbUnit)


if __name__ == "__main__":
    pytest.main()
