import json
import os
from tempfile import TemporaryDirectory

import pytest
from csvcubed.cli.build import build as cli_build
from csvcubed.readers.cubeconfig.v1_0.configdeserialiser import *
from csvcubed.readers.cubeconfig.schema_versions import QubeConfigJsonSchemaVersion

from tests.unit.test_baseunit import get_test_cases_dir
from definitions import ROOT_DIR_PATH

TEST_CASE_DIR = get_test_cases_dir().absolute() / "readers" / "cube-config" / "v1.0"
SCHEMA_PATH_FILE = Path(ROOT_DIR_PATH, "csvcubed", "schema", "cube-config-schema.json")


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
    test_data_path = Path(
        os.path.join(TEST_CASE_DIR, "cube_data_convention_ok.csv")
    ).resolve()
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
    assert isinstance(
        col_dim_0.structural_definition.code_list.metadata, CatalogMetadata
    )
    assert isinstance(col_dim_0.structural_definition.code_list.concepts, list)
    assert isinstance(
        col_dim_0.structural_definition.code_list.concepts[0], NewQbConcept
    )

    col_dim_1 = cube.columns[1]
    assert isinstance(col_dim_1.structural_definition, NewQbDimension)
    assert isinstance(
        col_dim_1.structural_definition.code_list.metadata, CatalogMetadata
    )
    assert isinstance(col_dim_1.structural_definition.code_list.concepts, list)
    assert isinstance(
        col_dim_1.structural_definition.code_list.concepts[0], NewQbConcept
    )

    col_observation = cube.columns[2]
    assert isinstance(
        col_observation.structural_definition, QbMultiMeasureObservationValue
    )
    assert col_observation.structural_definition.unit is None
    assert col_observation.structural_definition.data_type == "decimal"

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
        col_attribute.structural_definition.code_list.concepts[0], NewQbConcept
    )


def test_conventional_column_ordering_correct():
    """
    Ensure that the ordering of columns is as in the CSV.
    """

    with TemporaryDirectory() as t:
        temp_dir = Path(t)

        cube_config = {"columns": {"Amount": {"type": "observations"}}}
        # Defining the configured column in the middle of conventional columns to test ordering.
        data = pd.DataFrame(
            {
                "Dimension 1": ["A", "B", "C"],
                "Amount": [1.0, 2.0, 3.0],
                "Dimension 2": ["D", "E", "F"],
            }
        )

        data_file_path = temp_dir / "data.csv"
        config_file_path = temp_dir / "config.json"

        with open(config_file_path, "w+") as config_file:
            json.dump(cube_config, config_file, indent=4)

        data.to_csv(str(data_file_path), index=False)

        deserialiser = get_deserialiser(
            SCHEMA_PATH_FILE, QubeConfigJsonSchemaVersion.V1_0.value
        )

        cube, _ = deserialiser(data_file_path, config_file_path)

        column_titles_in_order = [c.csv_column_title for c in cube.columns]
        assert column_titles_in_order == list(data.columns)


if __name__ == "__main__":
    pytest.main()
