import os
import pytest

from csvcubed.readers.configdeserialiser import *
from tests.unit.test_baseunit import get_test_cases_dir

PROJECT_ROOT = Path(Path(__file__).parent, "..", "..", "..", "..").resolve()
TEST_CASE_DIR = Path(get_test_cases_dir().absolute(), 'config')
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

def test_02_dimension_new_ok():
    """
    Populates all options and confirms the New Dimension & CodeList classes are created
    and all properties are mapped through correctly
    """
    column_data = ['a', 'b', 'c', 'a']
    dimension_config = {
        'type': 'dimension',
        'label': 'The New Dimension',
        'description': 'A description of the dimension',
        'from_existing': 'http://gss-cogs/dimesions/#period',
        'definition_uri': 'http://wikipedia.com/#periods',
        'cell_uri_template': 'http://example.org/code-list/{+some_column}',
        # 'code_list': '', -> defaults to True so should be a NewQbCodeList
    }
    data = pd.Series(column_data, name='Dimension Heading')
    parent_dir = Path(__file__).parent
    column = map_column_to_qb_component('New Dimension', dimension_config, data, parent_dir)


    # Confirm a Column is returned
    assert isinstance(column, QbColumn)
    # And the Column is of the expected type
    assert isinstance(column.structural_definition, NewQbDimension)

    # Check code_list default constructions (from data)
    assert isinstance(column.structural_definition.code_list, NewQbCodeList)
    assert isinstance(column.structural_definition.code_list.metadata, CatalogMetadata)
    assert hasattr(column, 'type') is False
    assert column.structural_definition.label == dimension_config['label']
    assert column.structural_definition.description == dimension_config['description']
    assert column.structural_definition.parent_dimension_uri == dimension_config['from_existing']
    assert column.structural_definition.source_uri == dimension_config['definition_uri']

    assert isinstance(column.structural_definition.code_list.concepts, list)
    assert isinstance(column.structural_definition.code_list.concepts[0], NewQbConcept)
    assert column.csv_column_uri_template == dimension_config['cell_uri_template']

    unique_column_data = list(sorted(set(column_data)))
    assert len(column.structural_definition.code_list.concepts) == len(unique_column_data)
    for concept in column.structural_definition.code_list.concepts:
        assert concept.label in unique_column_data
        assert concept.code in unique_column_data
        assert concept.description is None
        assert concept.parent_code is None
        assert concept.sort_order is None
        assert concept.uri_safe_identifier == uri_safe(concept.label)
        assert concept.uri_safe_identifier_override is None


def test_03_dimension_existing_ok():
    """
    Populates options for an Existing Dimension & New CodeList classes are created
    and all properties are mapped through correctly
    """
    column_data = ['a', 'b', 'c', 'a']
    dimension_config = {
        'type': 'dimension',
        'from_existing': 'http://gss-cogs/dimesions/#period',
        'cell_uri_template': 'http://example.org/code-list/{+some_column}',
    }
    data = pd.Series(column_data, name='Dimension Heading')
    parent_dir = Path(__file__).parent
    column = map_column_to_qb_component('New Dimension', dimension_config, data, parent_dir)

    # Confirm a Column is returned
    assert isinstance(column, QbColumn)
    assert hasattr(column, 'type') is False

    # And the Column is of the expected type
    assert isinstance(column.structural_definition, ExistingQbDimension)
    assert not hasattr(column.structural_definition, 'code_list')
    assert column.structural_definition.dimension_uri == dimension_config['from_existing']
    assert column.structural_definition.range_uri is None
    assert isinstance(column.structural_definition.arbitrary_rdf, list)
    assert column.structural_definition.arbitrary_rdf == []


if __name__ == "__main__":
    pytest.main()
