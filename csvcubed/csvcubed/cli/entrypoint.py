"""
CLI
---

The *Command Line Interface* for `csvcubed inspect`.
"""


import click
import logging
from pathlib import Path

from csvcubed.cli.inspect.inspect import inspect

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

_logger = logging.getLogger(__name__)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def entry_point():
    """
    csvcubed - a tool to generate qb-flavoured CSV-W cubes from COGS-style info.json files.
    """


# csvcubed build command goes here


@entry_point.command("inspect")
@click.argument(
    "csvw_metadata_json_path",
    type=click.Path(exists=True, path_type=Path),
    metavar="TIDY_CSV-W_METADATA_JSON_PATH",
)
def inspect_command(csvw_metadata_json_path: Path) -> None:
    _logger.info(
        f"Valid csv-w metadata json path: {csvw_metadata_json_path.absolute()}"
    )
    inspect(csvw_metadata_json_path)
