import os
import pytest
from csvcubed.readers.configdeserialiser import *
from csvcubed.readers.configdeserialiser import _load_resource


PROJECT_ROOT = os.path.realpath(
    os.path.join(os.path.split(__file__)[0], "..", "..", "..", "..")
)
TEST_CASE_DIR = os.path.join(PROJECT_ROOT, "tests", "test-cases", "config")
SCHEMA_PATH_FILE = os.path.realpath(
    os.path.join(PROJECT_ROOT, "csvcubed", "schema", "cube-config-schema.json")
)
SCHEMA_PATH_URI = "http://gss-cogs.github.io/family-schemas/dataset-schema-1.1.0.json"


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

def test_build_98():
    """
    Valid Cube from using config.json
    """
    test_case_data = Path(os.path.join(TEST_CASE_DIR, 'cube_data_config_ok.csv')).resolve()
    test_case_config = Path(os.path.join(TEST_CASE_DIR, 'cube_data_config_ok.json')).resolve()
    test_case_json = None
    print(f"test_case_data: {test_case_data}")
    print(f"test_case_config: {test_case_config}")
    cube, validation_errors = build(csv_path=test_case_data, config_json=test_case_config)
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, List)


def test_build_99():
    """
    Valid Cube from Data using Convention (no config json)
    """
    test_case_data = Path(os.path.join(TEST_CASE_DIR, 'cube_data_convention_ok.csv')).resolve()
    test_case_json = None
    print(f"test_case_data: {test_case_data}")
    cube, validation_errors = build(csv_path=test_case_data)
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, List)
    print("*******************************")
    cj = cube.as_dict()
    print(cj)
    print("*******************************")


if __name__ == "__main__":
    pytest.main()
