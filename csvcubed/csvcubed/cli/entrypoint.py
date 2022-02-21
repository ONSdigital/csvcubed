"""
CLI
---
The *Command Line Interface* for :mod:`~csvcubed.csvcubedcli.infojson2csvqb`.
"""
import logging
import sys
import click
from pathlib import Path
from csvcubed.utils.log import handle_exception, start_logging

from .build import build


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def entry_point():
    """
    csvcubed - a tool to generate qb-flavoured CSV-W cubes from qube-config files.
    """


@entry_point.command("build")
@click.option(
    "--config",
    "-c",
    help="Location of the json file containing the qube-config file.",
    type=click.Path(exists=True, path_type=Path, file_okay=True, dir_okay=False),
    required=True,
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
    "--logdir", 
    help="Location for log files.", 
    type=str, 
    default="csvcubedcli"
)
@click.option(
    "--logginglvl",
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
    logdir: str,
    logginglvl: str,
    fail_when_validation_error: bool,
    validation_errors_to_file: bool,
):
    """Build a qb-flavoured CSV-W from a tidy CSV."""
    validation_errors_file_out = (
        out / "validation-errors.json" if validation_errors_to_file else None
    )
    out.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(__name__)
    start_logging(
        logdir=logdir,
        selected_logging_level=logginglvl,
    )
    try:
        build(
            config=config,
            output_directory=out,
            csv_path=csv,
            fail_when_validation_error_occurs=fail_when_validation_error,
            validation_errors_file_out=validation_errors_file_out,
        )
    except Exception:
        handle_exception(logger, *sys.exc_info())

        