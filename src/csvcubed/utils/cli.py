"""
CLI
---

Contains methods to log validation and JSON schema errors to file.
"""

import dataclasses
import json
import logging
from pathlib import Path
from typing import List, Optional

from csvcubedmodels.dataclassbase import DataClassBase

from csvcubed.cli.error_mapping import friendly_error_mapping
from csvcubed.models.errorurl import HasErrorUrl
from csvcubed.models.jsonvalidationerrors import JsonSchemaValidationError
from csvcubed.models.validationerror import ValidationError
from csvcubed.utils.json import serialize_sets

_logger = logging.getLogger(__name__)


def log_validation_and_json_schema_errors(
    output_directory: Path,
    validation_errors: List[ValidationError],
    json_schema_validation_errors: List[JsonSchemaValidationError],
    validation_errors_file_name: Optional[str] = None,
    fail_when_validation_error_occurs: bool = False,
):
    """Log and write validation and JSON schema errors to a specified file loaction"""
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


def _validation_error_to_display_json_dict(error: ValidationError) -> dict:
    dict_value: dict
    if isinstance(error, DataClassBase):
        dict_value = error.as_json_dict()
    else:
        dict_value = dataclasses.asdict(error)

    return dict_value
