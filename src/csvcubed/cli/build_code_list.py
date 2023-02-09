"""
Build Code List Command
-------------
Build a qb-flavoured CSV-W from a code list config.json
"""

import logging
from os import getcwd
from pathlib import Path
from typing import List, Optional, Tuple

from csvcubed.models.codelistconfig.code_list_config import CodeListConfig
from csvcubed.models.cube.qb.components import NewQbCodeList
from csvcubed.readers.cubeconfig.utils import load_resource
from csvcubed.utils.validators.schema import (
    map_to_internal_validation_errors,
    validate_dict_against_schema,
)
from csvcubed.writers.qbwriter import QbWriter
from csvcubed.writers.skoscodelistwriter import SkosCodeListWriter
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "readers" / "code-list-config" / "v1.0"

_logger = logging.getLogger(__name__)

# csvcubed code-list build <some-config-file.json>


def command():

    code_list_config_path = _test_case_base_dir / "code_list_config_hierarchical.json"

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


def build_code_list(
    config_path: Optional[Path] = None,
    output_directory: Path = Path(".", "out").resolve(),
):

    if not output_directory.exists():
        _logger.debug("Creating output directory %s", output_directory.absolute())
        output_directory.mkdir(parents=True)

    the_data = command()
    try:
        writer = SkosCodeListWriter(the_data[0])
        writer.write(output_directory)
    except:
        _logger.fatal("Failed to generate CSV-W.")
        raise

    print(f"Build Complete @ {output_directory.resolve()}")
    return
