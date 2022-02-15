"""
CLI
---

The *Command Line Interface* for `csvcubed inspect`.
"""

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
    "json",
    type=click.Path(exists=True, path_type=Path),
    metavar="TIDY_CSV-W_METADATA_JSON_PATH",
)
def inspect_command(json: Path) -> None:
    inspect(metadata_json=json)
