"""
Build Command
-------------
Build a qb-flavoured CSV-W from a config.json and a tidy CSV.
"""
import dataclasses
import json
import logging
from pathlib import Path
from typing import Optional

from csvcubed.cli.error_mapping import friendly_error_mapping
from csvcubed.readers.cubeconfig.get_deserialiser import get_deserialiser
from csvcubedmodels.dataclassbase import DataClassBase
from csvcubed.utils.qb.validation.cube import validate_qb_component_constraints


_logger = logging.getLogger(__name__)


def build(
    csv_path: Path,
    config_path: Optional[Path] = None,
    output_directory: Path = Path(".", "out").resolve(),
    fail_when_validation_error_occurs: bool = False,
    validation_errors_file_out: Optional[Path] = None,
):
    _logger.debug(f"CSV: {csv_path.absolute() if csv_path is not None else ''}")
    _logger.debug(
        f"qube-config.json: {config_path.absolute() if config_path is not None else ''}"
    )

    deserialiser = get_deserialiser(config_path)
    cube, json_schema_validation_errors = deserialiser(csv_path, config_path)

    validation_errors = cube.validate()
    validation_errors += validate_qb_component_constraints(cube)

    if not output_directory.exists():
        _logger.debug(f"Creating output directory {output_directory.absolute()}")
        output_directory.mkdir(parents=True)

    if len(validation_errors) > 0 or len(json_schema_validation_errors) > 0:
        for error in validation_errors:
            message = friendly_error_mapping(error)
            _logger.error(f"Validation Error: {message}")

        for err in json_schema_validation_errors:
            _logger.warning(f"Schema Validation Error: {err.message}")

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

            with open(output_directory / validation_errors_file_out, "w+") as f:
                json.dump(all_errors, f, indent=4, default=serialize_sets)

        if fail_when_validation_error_occurs and len(validation_errors) > 0:
            exit(1)

    print(f"Build Complete")
    return cube, validation_errors


# Credit: Antti Haapala: https://stackoverflow.com/questions/8230315/how-to-json-serialize-sets
def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)

    return obj