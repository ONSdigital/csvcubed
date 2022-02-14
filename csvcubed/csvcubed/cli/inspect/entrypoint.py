"""
CLI
---

The *Command Line Interface* for :csvcubed:`~csvcubed.csvcubed.cli.inspect`.
"""

from pathlib import Path
import click
from csvcubed.cli.inspect.inspect import inpsect

from csvcubed.cli.inspect.metadatainputhandler import MetadataInputHandler


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def entry_point() -> None:
    """
    csvcubed inspect - a CLI tool to validate CSV-W metadata files.

    Member of :file:`./entrypoint.py`

    :return: `None`
    """


@entry_point.command("inspect")
@click.argument(
    "csv", type=click.Path(exists=True, path_type=Path), metavar="TIDY_CSV_PATH"
)
def inspect_command(metadata_json: Path) -> None:
    inpsect(metadata_json)

