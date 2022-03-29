"""
Build Command
-------------
Build a qb-flavoured CSV-W from a config.json and a tidy CSV.
"""
import dataclasses
import json
import logging
from pathlib import Path
from typing import Optional, Tuple, List

from csvcubedmodels.dataclassbase import DataClassBase

from csvcubed.models.cube import QbCube
from csvcubed.models.validationerror import SpecificValidationError, ValidationError
from csvcubed.readers.cubeconfig.schema_versions import (
    QubeConfigDeserialiser,
    get_deserialiser_for_schema,
)
from csvcubed.readers.cubeconfig.utils import load_resource
from csvcubed.utils.qb.validation.cube import validate_qb_component_constraints
from csvcubed.writers.qbwriter import QbWriter

_logger = logging.getLogger(__name__)


def build(
    csv_path: Path,
    config_path: Optional[Path] = None,
    output_directory: Path = Path(".", "out").resolve(),
    fail_when_validation_error_occurs: bool = False,
    validation_errors_file_out: Optional[Path] = None,
) -> Tuple[QbCube, List[ValidationError]]:
    _logger.debug("CSV: %s", csv_path.absolute() if csv_path is not None else "")
    _logger.debug(
        "qube-config.json: %s",
        config_path.absolute() if config_path is not None else "",
    )

    deserialiser = _get_versioned_deserialiser(config_path)
    cube, json_schema_validation_errors = deserialiser(csv_path, config_path)

    validation_errors = cube.validate()
    validation_errors += validate_qb_component_constraints(cube)

    if not output_directory.exists():
        _logger.debug("Creating output directory %s", output_directory.absolute())
        output_directory.mkdir(parents=True)

    if len(validation_errors) > 0 or len(json_schema_validation_errors) > 0:
        for error in validation_errors:
            _logger.error("Validation Error: %s", error.message)
            if isinstance(error, SpecificValidationError):
                _logger.error("More information: %s", error.get_error_url())

        for err in json_schema_validation_errors:
            _logger.warning("Schema Validation Error: %s", err.message)

        if validation_errors_file_out is not None:
            validation_errors_dict = [
                e.as_json_dict()
                if isinstance(e, DataClassBase)
                else dataclasses.asdict(e)
                for e in validation_errors
            ]
            all_errors = validation_errors_dict + [
                e.message for e in json_schema_validation_errors
            ]

            with open(validation_errors_file_out, "w+") as f:
                json.dump(all_errors, f, indent=4)

        if fail_when_validation_error_occurs and len(validation_errors) > 0:
            exit(1)

    writer = QbWriter(cube)
    writer.write(output_directory)

    print(f"Build Complete")
    return cube, validation_errors


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
