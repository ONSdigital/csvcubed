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
@click.option("--disableuriwarning", "-d",default = False)
def _replace(input, output, value, disableuriwarning):
    """
    Replace instances of values with other values across a given file.
    """
    urireplacement._replace(input=input, output=output, values=value, disableuriwarning=disableuriwarning)
