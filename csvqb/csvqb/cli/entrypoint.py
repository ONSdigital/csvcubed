"""
CLI
---

The *Command Line Interface* for :mod:`csvqb`.
"""
import click
from pathlib import Path
import colorama

from .build import build


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def entry_point():
    """
    CSVqb - a tool to generate qb-flavoured CSV-W cubes.
    """
    colorama.init(autoreset=True, wrap=True)


@entry_point.command("build")
@click.option(
    "--config",
    "-c",
    help="Location of the info.json file containing the QB column mapping definitions.",
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
    help="Save validation errors to an `validation-errors.json` file in the output directory.",
    flag_value=True,
    default=False,
    show_default=True,
)
@click.argument(
    "csv", type=click.Path(exists=True, path_type=Path), metavar="TIDY_CSV_PATH"
)
def build_command(
    config: Path,
    out: Path,
    csv: Path,
    fail_when_validation_error: bool,
    validation_errors_to_file: bool,
):
    """Build a qb-flavoured CSV-W from a tidy CSV."""
    validation_errors_file_out = (
        out / "validation-errors.json" if validation_errors_to_file else None
    )
    build(config, out, csv, fail_when_validation_error, validation_errors_file_out)
