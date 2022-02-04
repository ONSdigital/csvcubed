"""
Build Command
-------------
Build a qb-flavoured CSV-W from an info.json and a tidy CSV.
"""
from appdirs import AppDirs
from pathlib import Path
from typing import Optional


def build(
    info_json: Path,
    catalog_metadata_json_file: Optional[Path],
    output_directory: Path,
    csv_path: Path,
    fail_when_validation_error_occurs: bool,
    validation_errors_file_out: Optional[Path],
):
    print(f"CSV: {csv_path.absolute()}")
    print(f"info.json: {info_json.absolute()}")
