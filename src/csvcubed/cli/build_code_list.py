"""
Build Code List Command
-------------
Build a qb-flavoured CSV-W from a code list config.json
"""

import logging
from pathlib import Path
from typing import Optional

from csvcubed.readers.codelistconfig.codelist_schema_versions import (
    CodeListConfigDeserialiser,
    get_deserialiser_for_code_list_schema,
)
from csvcubed.readers.cubeconfig.utils import load_resource
from csvcubed.utils.cli import log_validation_and_json_schema_errors
from csvcubed.writers.skoscodelistwriter import SkosCodeListWriter

_logger = logging.getLogger(__name__)

# csvcubed code-list build <some-config-file.json>


def build_code_list(
    config_path: Path,
    output_directory: Path,
    fail_when_validation_error_occurs: bool = False,
    validation_errors_file_name: Optional[str] = None,
):

    code_list_deserialiser = get_code_list_versioned_deserialiser(config_path)

    (
        code_list,
        json_schema_validation_errors,
        validation_errors,
    ) = code_list_deserialiser(config_path)

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
