"""
Build Code List Command
-------------
Build a qb-flavoured CSV-W from a code list config.json
"""

import dataclasses
import json
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from csvcubedmodels.dataclassbase import DataClassBase

from csvcubed.cli.error_mapping import friendly_error_mapping
from csvcubed.models.codelistconfig.code_list_config import CodeListConfig
from csvcubed.models.cube.qb.components import NewQbCodeList
from csvcubed.models.errorurl import HasErrorUrl
from csvcubed.models.jsonvalidationerrors import JsonSchemaValidationError
from csvcubed.models.validationerror import ValidationError
from csvcubed.readers.cubeconfig.utils import load_resource
from csvcubed.utils.json import serialize_sets
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
    (
        code_list,
        json_schema_validation_errors,
        validation_errors,
    ) = _extract_and_validate_code_list(config_path)

    if not output_directory.exists():
        _logger.debug("Creating output directory %s", output_directory.absolute())
        output_directory.mkdir(parents=True)

    if any(validation_errors) or any(json_schema_validation_errors):
        _write_errors_to_log(json_schema_validation_errors, validation_errors)

        if validation_errors_file_name is not None:
            all_errors: List[ValidationError] = (
                validation_errors + json_schema_validation_errors  # type: ignore
            )
            all_errors_dict = [
                _validation_error_to_display_json_dict(e) for e in all_errors
            ]

            with open(output_directory / validation_errors_file_name, "w+") as f:
                json.dump(all_errors_dict, f, indent=4, default=serialize_sets)

        if any(validation_errors):
            if fail_when_validation_error_occurs:
                exit(1)
            else:
                _logger.warning(
                    "Attempting to build CSV-W even though there are %s validation errors.",
                    len(validation_errors),
                )

    try:
        writer = SkosCodeListWriter(code_list)
        writer.write(output_directory)
    except:
        _logger.fatal("Failed to generate CSV-W.")
        raise

    print(f"Build Complete @ {output_directory.resolve()}")
    return


def _validation_error_to_display_json_dict(error: ValidationError) -> dict:
    dict_value: dict
    if isinstance(error, DataClassBase):
        dict_value = error.as_json_dict()
    else:
        dict_value = dataclasses.asdict(error)

    return dict_value


def _write_errors_to_log(
    json_schema_validation_errors: List[JsonSchemaValidationError],
    validation_errors: List[ValidationError],
    schema_validation_errors_depth: int = 2,
) -> None:
    for error in validation_errors:
        _logger.error("Validation Error: %s", friendly_error_mapping(error))
        if isinstance(error, HasErrorUrl):
            _logger.error("More information: %s", error.get_error_url())

    for err in json_schema_validation_errors:
        _logger.warning(
            "Schema Validation Error: %s",
            err.to_display_string(depth_to_display=schema_validation_errors_depth),
        )
