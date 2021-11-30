"""
__INIT__ URI REPLACE
--------------------

Functionality to use the command line to specify what ttl files need uris replaced, and which uris are to be found and replaced with.
"""
from pathlib import Path
from typing import Any
import click

import csvcubedpmd.urireplacement.urireplacement as urireplacement


@click.group("uri")
def uri_group():
    """
    Work with URIs.
    """
    pass


@uri_group.command("replace")
@click.argument("input", type=click.Path())
@click.argument("output", type=click.Path())
@click.option("--value", "-v", nargs=2, multiple=True)
@click.option("--force", is_flag=True, default=False)
def _replace(input: click.Path, output: click.Path, value: list[tuple[str, str]], force: bool):
    """
    Replace instances of values with other values across a given file.
    """
    urireplacement._replace(input=input, output=output, values=value, force=force)
