"""
Build Command
-------------
Build a qb-flavoured CSV-W from an info.json and a tidy CSV.
"""
import logging
from pathlib import Path
from typing import Optional


def build(
    config: Path,
    output_directory: Path,
    csv_path: Path,
    fail_when_validation_error_occurs: bool,
    validation_errors_file_out: Optional[Path],
    root_logger_name: str
):

    # Create a path to save the validation-errors.json file in the ./out directory

    logger = logging.getLogger(root_logger_name)
    logger.debug(f"CSV: {csv_path.absolute()}")
    logger.debug(f"qube-config.json: {config.absolute()}")
