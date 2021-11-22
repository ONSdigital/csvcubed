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
@click.option("--force",is_flag = True) # TODO: Convert to flag
def _replace(input, output, value, force):
    """
    Replace instances of values with other values across a given file.
    """
    urireplacement._replace(input=input, output=output, values=value, force=force)
