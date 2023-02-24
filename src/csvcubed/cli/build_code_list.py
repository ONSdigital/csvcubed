"""
Build Code List Command
-----------------------
Build a qb-flavoured CSV-W from a code list config.json
"""

import logging
from pathlib import Path
from typing import Optional

from csvcubed.readers.codelistconfig.codelist_schema_versions import (
    get_code_list_versioned_deserialiser,
)
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
