"""
Build Command
-------------
Build a qb-flavoured CSV-W from an info.json and a tidy CSV.
"""
import dataclasses
import json

from colorama import Fore, Style
from pathlib import Path
import pandas as pd
from typing import Optional
from csvcubed.writers.qbwriter import QbWriter
from csvcubed.utils.qb.validation.cube import validate_qb_component_constraints
from csvcubed.models.cube import SpecificValidationError
from csvcubed.models.cube.qb import QbCube
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubedmodels.dataclassbase import DataClassBase

from csvcubed.csvcubedcli.configloaders.infojson import get_cube_from_info_json


def build(
    info_json: Path,
    catalog_metadata_json_file: Optional[Path],
    output_directory: Path,
    csv_path: Path,
    fail_when_validation_error_occurs: bool,
    validation_errors_file_out: Optional[Path],
):
    print(f"{Style.DIM}CSV: {csv_path.absolute()}")
    print(f"{Style.DIM}info.json: {info_json.absolute()}")
    data = pd.read_csv(csv_path)
    assert isinstance(data, pd.DataFrame)
    cube, json_schema_validation_errors = get_cube_from_info_json(info_json, data)

    if catalog_metadata_json_file is not None:
        _override_catalog_metadata_state(catalog_metadata_json_file, cube)

    validation_errors = cube.validate()
    validation_errors += validate_qb_component_constraints(cube)

    if not output_directory.exists():
        print(f"Creating output directory {output_directory.absolute()}")
        output_directory.mkdir()

    if len(validation_errors) > 0 or len(json_schema_validation_errors) > 0:
        for error in validation_errors:
            print(f"{Fore.RED + Style.BRIGHT}Validation Error: {Style.NORMAL + error.message}")
            if isinstance(error, SpecificValidationError):
                print(f"More information: {error.get_error_url()}")

        for err in json_schema_validation_errors:
            print(
                f"{Fore.LIGHTRED_EX + Style.BRIGHT}Schema Validation Error: {Style.NORMAL + err.message}"
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

    qb_writer = QbWriter(cube)
    qb_writer.write(output_directory)

    print(f"{Fore.GREEN + Style.BRIGHT}Build Complete")


def _override_catalog_metadata_state(
    catalog_metadata_json_file: Path, cube: QbCube
) -> None:
    with open(catalog_metadata_json_file, "r") as f:
        catalog_metadata_dict: dict = json.load(f)
    overriding_catalog_metadata = CatalogMetadata.from_dict(catalog_metadata_dict)
    cube.metadata.override_with(
        overriding_catalog_metadata,
        overriding_keys={k for k in catalog_metadata_dict.keys()},
    )