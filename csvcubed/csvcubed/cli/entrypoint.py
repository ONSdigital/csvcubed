"""
CLI
---
The *Command Line Interface* for :mod:`~csvcubed.cli`.
"""
import logging
import sys
from pathlib import Path

import click

from csvcubed.utils.log import log_exception, start_logging
from csvcubed.cli.inspect.inspect import inspect
from csvcubed.cli.build import build
from csvcubed.models.errorurl import HasErrorUrl


_logger = logging.getLogger(__name__)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def entry_point():
    """
    csvcubed - a tool to generate qb-flavoured CSV-W cubes from COGS-style info.json files.
    """


@entry_point.command("build")
@click.option(
    "--config",
    "-c",
    help="Location of the json file containing the qube-config file.",
    type=click.Path(exists=True, path_type=Path, file_okay=True, dir_okay=False),
    required=False,
    metavar="CONFIG_PATH",
)
@click.option(
    "--out",
    "-o",
    help="Location of the CSV-W outputs.",
    default="./out",
    show_default=True,
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    metavar="OUT_DIR",
)
@click.option(
    "--fail-when-validation-error/--ignore-validation-errors",
    help="Fail when validation errors occur or ignore validation errors and continue generating a CSV-W.",
    default=True,
    show_default=True,
)
@click.option(
    "--validation-errors-to-file",
    "validation_errors_to_file",
    help="Save validation errors to a `validation-errors.json` file in the output directory.",
    flag_value=True,
    default=False,
    show_default=True,
)
@click.option(
    "--log-level",
    help="select a logging level out of: 'warn', 'err', 'crit', 'info' or 'debug'.",
    type=click.Choice(["warn", "err", "crit", "info", "debug"], case_sensitive=False),
    default="warn",
)
@click.argument(
    "csv", type=click.Path(exists=True, path_type=Path), metavar="TIDY_CSV_PATH"
)
def build_command(
    config: Path,
    out: Path,
    csv: Path,
    log_level: str,
    fail_when_validation_error: bool,
    validation_errors_to_file: bool,
):
    """Build a qb-flavoured CSV-W from a tidy CSV."""
    validation_errors_file_out = (
        out / "validation-errors.json" if validation_errors_to_file else None
    )
    out.mkdir(parents=True, exist_ok=True)

    start_logging(log_dir_name="csvcubed-cli", selected_logging_level=log_level)
    try:
        build(
            config_path=config,
            output_directory=out,
            csv_path=csv,
            fail_when_validation_error_occurs=fail_when_validation_error,
            validation_errors_file_out=validation_errors_file_out,
        )

    except Exception as e:
        log_exception(_logger, e)
        sys.exit(1)


@entry_point.command("inspect")
@click.option(
    "--log-level",
    help="select a logging level out of: 'warn', 'err', 'crit', 'info' or 'debug'.",
    type=click.Choice(["warn", "err", "crit", "info", "debug"], case_sensitive=False),
    default="warn",
)
@click.argument(
    "csvw_metadata_json_path",
    type=click.Path(exists=True, path_type=Path),
    metavar="TIDY_CSV-W_METADATA_JSON_PATH",
)
def inspect_command(log_level: str, csvw_metadata_json_path: Path) -> None:
    """inspect the contents of a CSV-W generated with csvcubed"""
    start_logging(log_dir_name="csvcubed-cli", selected_logging_level=log_level)
    try:
        inspect(csvw_metadata_json_path)
    except Exception as e:
        log_exception(_logger, e)
        if isinstance(e, HasErrorUrl):
            _logger.error(f"More information available at {e.get_error_url()}")
        sys.exit(1)
