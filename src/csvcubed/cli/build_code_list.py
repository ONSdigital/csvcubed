"""
Build Code List Command
-----------------------
Build a qb-flavoured CSV-W from a code list config.json
"""

import logging
from pathlib import Path
from typing import Optional, Union

from csvcubed.readers.codelistconfig.codelist_schema_versions import (
    LATEST_CODELIST_SCHEMA_URL,
    CodeListConfigDeserialiser,
    get_deserialiser_for_code_list_schema,
)
from csvcubed.readers.cubeconfig.utils import load_resource
from csvcubed.utils.cli import log_validation_and_json_schema_errors
from csvcubed.writers.skoscodelistwriter import SkosCodeListWriter

_logger = logging.getLogger(__name__)


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
        _logger.critical(
            "Failed to generate CSV-W. Did not update outputs in %s",
            output_directory,
        )
        raise

    print(f"Build Complete @ {output_directory.resolve()}")


def get_code_list_versioned_deserialiser(
    json_config_path_or_dict: Optional[Union[Path, dict]],
    default_schema_uri: str = LATEST_CODELIST_SCHEMA_URL,
) -> CodeListConfigDeserialiser:
    """
    Return the correct version of the config deserialiser based on the schema in the code list config file
    """
    if json_config_path_or_dict:
        if isinstance(json_config_path_or_dict, Path):
            config = load_resource(json_config_path_or_dict)
        else:
            config = json_config_path_or_dict
        return get_deserialiser_for_code_list_schema(
            config.get("$schema"), default_schema_uri
        )
    else:
        return get_deserialiser_for_code_list_schema(None, default_schema_uri)
