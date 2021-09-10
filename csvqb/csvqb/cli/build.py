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

from csvqb.configloaders.infojson import get_cube_from_info_json
from csvqb.writers.qbwriter import QbWriter
from csvqb.utils.qb.cube import validate_qb_component_constraints
from csvqb.models.cube.qb import QbCube
from csvqb.models.cube.qb.catalog import CatalogMetadata


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
    cube = get_cube_from_info_json(info_json, data)

    if catalog_metadata_json_file is not None:
        _override_catalog_metadata_state(catalog_metadata_json_file, cube)

    errors = cube.validate()
    errors += validate_qb_component_constraints(cube)

    if not output_directory.exists():
        print(f"Creating output directory {output_directory.absolute()}")
        output_directory.mkdir()

    if len(errors) > 0:
        for error in errors:
            print(
                f"{Fore.RED + Style.BRIGHT}Validation Error: {Style.NORMAL + error.message}"
            )

        if validation_errors_file_out is not None:
            with open(validation_errors_file_out, "w+") as f:
                json.dump([dataclasses.asdict(e) for e in errors], f, indent=4)

        if fail_when_validation_error_occurs:
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
        overriding_catalog_metadata, overriding_keys=catalog_metadata_dict.keys()
    )
