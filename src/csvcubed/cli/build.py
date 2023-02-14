"""
Build Command
-------------
Build a qb-flavoured CSV-W from a config.json and a tidy CSV.
"""
import dataclasses
import json
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from csvcubedmodels.dataclassbase import DataClassBase

from csvcubed.cli.error_mapping import friendly_error_mapping
from csvcubed.models.cube.cube import QbCube
from csvcubed.models.errorurl import HasErrorUrl
from csvcubed.models.jsonvalidationerrors import JsonSchemaValidationError
from csvcubed.models.validationerror import ValidationError
from csvcubed.readers.cubeconfig.schema_versions import (
    QubeConfigDeserialiser,
    get_deserialiser_for_schema,
)
from csvcubed.readers.cubeconfig.utils import load_resource
from csvcubed.utils.json import serialize_sets
from csvcubed.utils.qb.validation.cube import validate_qb_component_constraints
from csvcubed.writers.qbwriter import QbWriter

_logger = logging.getLogger(__name__)


def build(
    csv_path: Path,
    config_path: Optional[Path] = None,
    output_directory: Path = Path(".", "out").resolve(),
    fail_when_validation_error_occurs: bool = False,
    validation_errors_file_name: Optional[str] = None,
) -> Tuple[QbCube, List[ValidationError]]:
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config_path, csv_path
    )

    if not output_directory.exists():
        _logger.debug("Creating output directory %s", output_directory.absolute())
        output_directory.mkdir(parents=True)

    if len(validation_errors) > 0 or len(json_schema_validation_errors) > 0:
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

        if len(validation_errors) > 0:
            if fail_when_validation_error_occurs:
                exit(1)
            else:
                _logger.warning(
                    "Attempting to build CSV-W even though there are %s validation errors.",
                    len(validation_errors),
                )

    try:
        writer = QbWriter(cube)
        writer.write(output_directory)
    except:
        _logger.fatal("Failed to generate CSV-W.")
        raise

    print(f"Build Complete @ {output_directory.resolve()}")
    return cube, validation_errors


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


def _extract_and_validate_cube(
    config_path: Optional[Path], csv_path: Path
) -> Tuple[QbCube, List[JsonSchemaValidationError], List[ValidationError]]:
    _logger.debug("CSV: %s", csv_path.absolute() if csv_path is not None else "")
    _logger.debug(
        "qube-config.json: %s",
        config_path.absolute() if config_path is not None else "",
    )

    deserialiser = _get_versioned_deserialiser(config_path)

    cube, json_schema_validation_errors, validation_errors = deserialiser(
        csv_path, config_path
    )

    validation_errors += cube.validate()
    validation_errors += validate_qb_component_constraints(cube)

    return cube, json_schema_validation_errors, validation_errors


def _get_versioned_deserialiser(
    json_config_path: Optional[Path],
) -> QubeConfigDeserialiser:
    """
    Return the correct version of the config deserialiser based on the schema in the cube config file
    """
    if json_config_path:
        config = load_resource(json_config_path)
        return get_deserialiser_for_schema(config.get("$schema"))
    else:
        return get_deserialiser_for_schema(None)
