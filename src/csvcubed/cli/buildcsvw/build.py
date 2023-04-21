"""
Build Command
-------------
Build a qb-flavoured CSV-W from a config.json and a tidy CSV.
"""
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from csvcubed.models.cube.cube import QbCube
from csvcubed.models.jsonvalidationerrors import JsonSchemaValidationError
from csvcubed.models.validationerror import ValidationError
from csvcubed.readers.cubeconfig.schema_versions import (
    QubeConfigDeserialiser,
    get_deserialiser_for_schema,
)
from csvcubed.readers.cubeconfig.utils import load_resource
from csvcubed.utils.cli import log_validation_and_json_schema_errors
from csvcubed.utils.qb.validation.cube import validate_qb_component_constraints
from csvcubed.writers.qbwriter import QbWriter

_logger = logging.getLogger(__name__)


def build_csvw(
    csv_path: Path,
    config_path: Optional[Path] = None,
    output_directory: Path = Path(".", "out").resolve(),
    fail_when_validation_error_occurs: bool = False,
    validation_errors_file_name: Optional[str] = None,
) -> Tuple[QbCube, List[ValidationError]]:
    cube, json_schema_validation_errors, validation_errors = _extract_and_validate_cube(
        config_path, csv_path
    )
    log_validation_and_json_schema_errors(
        output_directory,
        validation_errors,
        json_schema_validation_errors,
        validation_errors_file_name,
        fail_when_validation_error_occurs,
    )

    try:
        writer = QbWriter(cube)
        writer.write(output_directory)
    except:
        _logger.critical(
            "Failed to generate CSV-W. Did not update outputs in %s",
            output_directory,
        )
        raise

    print(f"Build Complete @ {output_directory.resolve()}")
    return cube, validation_errors


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

    validation_errors += cube.validate_all()
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
