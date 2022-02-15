"""
CLI
---

The *Command Line Interface* for `csvcubed inspect`.
"""

import logging
logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

from pathlib import Path
import click
import colorama

from .inspect import inspect


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def entry_point():
    """
    csvcubed - a tool to generate qb-flavoured CSV-W cubes from COGS-style info.json files.
    """
    colorama.init(autoreset=True, wrap=True)


# csvcubed build command goes here


@entry_point.command("inspect")
@click.argument(
    "csvw_metadata_json_path",
    type=click.Path(exists=True, path_type=Path),
    metavar="TIDY_CSV-W_METADATA_JSON_PATH",
)
def inspect_command(csvw_metadata_json_path: Path) -> None:
    inspect(csvw_metadata_json_path)
