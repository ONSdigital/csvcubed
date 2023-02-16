"""
Build Code List Command
-------------
Build a qb-flavoured CSV-W from a code list config.json
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

from csvcubed.models.codelistconfig.code_list_config import CodeListConfig
from csvcubed.models.cube.qb.components import NewQbCodeList
from csvcubed.models.jsonvalidationerrors import JsonSchemaValidationError
from csvcubed.models.validationerror import ValidationError
from csvcubed.readers.codelistconfig.codelist_schema_versions import (
    CodeListConfigDeserialiser,
    get_deserialiser_for_code_list_schema,
)
from csvcubed.readers.cubeconfig.utils import load_resource
from csvcubed.utils.cli import log_validation_and_json_schema_errors
from csvcubed.utils.validators.schema import (
    map_to_internal_validation_errors,
    validate_dict_against_schema,
)
from csvcubed.writers.skoscodelistwriter import SkosCodeListWriter

_logger = logging.getLogger(__name__)

# csvcubed code-list build <some-config-file.json>


def _extract_and_validate_code_list(
    code_list_config_path: Path,
) -> Tuple[NewQbCodeList, List[JsonSchemaValidationError], List[ValidationError]]:
    """Fill this in"""
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

    code_list = NewQbCodeList(
        code_list_config.metadata, code_list_config.new_qb_concepts
    )
    return (
        code_list,
        code_list_schema_validation_errors,
        code_list.pydantic_validation(),
    )


def build_code_list(
    config_path: Path,
    output_directory: Path,
    fail_when_validation_error_occurs: bool = False,
    validation_errors_file_name: Optional[str] = None,
):
    # (
    #     code_list,
    #     json_schema_validation_errors,
    #     validation_errors,
    # ) = _extract_and_validate_code_list(config_path)

    code_list_deserialiser = get_code_list_versioned_deserialiser(config_path)

    code_list, json_schema_validation_errors, validation_errors = sort_out(
        code_list_deserialiser, config_path
    )

    log_validation_and_json_schema_errors(
        output_directory,
        validation_errors,
        json_schema_validation_errors,
        validation_errors_file_name,
        fail_when_validation_error_occurs,
    )

    try:
        writer = SkosCodeListWriter(code_list)
        writer.write(output_directory)
    except:
        _logger.fatal("Failed to generate CSV-W.")
        raise

    print(f"Build Complete @ {output_directory.resolve()}")
    return


def get_code_list_versioned_deserialiser(
    json_config_path: Optional[Path],
) -> CodeListConfigDeserialiser:
    """
    Return the correct version of the config deserialiser based on the schema in the code list config file
    """
    if json_config_path:
        config = load_resource(json_config_path)
        return get_deserialiser_for_code_list_schema(config.get("$schema"))
    else:
        return get_deserialiser_for_code_list_schema(None)


def sort_out(
    the_data_we_need_now: CodeListConfigDeserialiser, config_path: Path
) -> Tuple[NewQbCodeList, List[JsonSchemaValidationError], List[ValidationError]]:

    code_list, json_schema_validation_errors, validation_errors = the_data_we_need_now(
        config_path
    )

    return code_list, json_schema_validation_errors, validation_errors
