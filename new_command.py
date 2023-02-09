from dataclasses import dataclass
from os import getcwd
from pathlib import Path

from csvcubed.models.codelistconfig.code_list_config import CodeListConfig
from csvcubed.models.cube.qb.components import NewQbCodeList
from csvcubed.readers.cubeconfig.utils import load_resource
from csvcubed.utils.validators.schema import (
    map_to_internal_validation_errors,
    validate_dict_against_schema,
)
from csvcubed.writers.skoscodelistwriter import SkosCodeListWriter
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "readers" / "code-list-config" / "v1.0"


def command(code_list_config_path: Path):

    code_list_config, code_list_config_dict = CodeListConfig.from_json_file(
        code_list_config_path
    )
    schema = load_resource(code_list_config.schema)

    unmapped_schema_validation_errors = validate_dict_against_schema(
        value=code_list_config_dict, schema=schema
    )

    code_list_schema_validation_errors = map_to_internal_validation_errors(
        schema, unmapped_schema_validation_errors
    )

    return (
        NewQbCodeList(code_list_config.metadata, code_list_config.new_qb_concepts),
        code_list_schema_validation_errors,
    )


def write_the_file():

    code_list_config_path = _test_case_base_dir / "code_list_config_hierarchical.json"

    the_data = command(code_list_config_path)
    the_writer = SkosCodeListWriter(the_data[0])
    path_to_out = getcwd() + "/out"

    the_writer.write(Path(path_to_out))
