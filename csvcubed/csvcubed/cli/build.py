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

from csvcubedmodels.dataclassbase import DataClassBase

from csvcubed.readers.configdeserialiser import (
    get_cube_from_data,
    get_cube_from_config_json
)
from csvcubed.utils.qb.validation.cube import validate_qb_component_constraints

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler())

def build(
    config: Path,
    output_directory: Path,
    csv_path: Path,
    fail_when_validation_error_occurs: bool,
    validation_errors_file_out: Optional[Path],
):

    # Create a path to save the validation-errors.json file in the ./out directory

    _logger.debug(f"CSV: {csv_path.absolute() if csv_path is not None else ''}")
    _logger.debug(f"qube-config.json: {config.absolute() if config is not None else ''}")

    if config:
        cube, json_schema_validation_errors = get_cube_from_config_json(config, csv_path)

    else:
        cube, json_schema_validation_errors = get_cube_from_data(csv_path)

    validation_errors = cube.validate()
    validation_errors += validate_qb_component_constraints(cube)

    if not output_directory.exists():
        print(f"Creating output directory {output_directory.absolute()}")
        output_directory.mkdir()

    if len(validation_errors) > 0 or len(json_schema_validation_errors) > 0:
        for error in validation_errors:
            print(
                f"Validation Error: {error.message}"
            )

        for err in json_schema_validation_errors:
            print(
                f"Schema Validation Error: {err.message}"
            )

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


    print(f"Build Complete")
    return cube, validation_errors