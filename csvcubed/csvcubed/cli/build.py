"""
Build Command
-------------
Build a qb-flavoured CSV-W from an info.json and a tidy CSV.
"""
from pathlib import Path
from typing import Optional


def build(
    config: Path,
    output_directory: Path,
    csv_path: Path,
    fail_when_validation_error_occurs: bool,
    validation_errors_file_out: Optional[Path],
):
    # Create a path to save the validation-errors.json file in the ./out directory


    print(f"CSV: {csv_path.absolute()}")
    print(f"qube-config.json: {config.absolute()}")
