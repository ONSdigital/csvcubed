from pathlib import Path
from typing import Any
import click

import csvcubedpmd.urireplacement.urireplacement as urireplacement
File = "/workspaces/csvwlib/csvcubed-pmd/tests/TurleTestFile.ttl"

@click.group("uri")
def uri_group():
    """
    Work with URIs.
    """
    pass


@uri_group.command('replace')
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def inout(input, output):
    """Copy contents of INPUT to OUTPUT."""
    while True:
        chunk = input.read(1024)
        if not chunk:
            break
        output.write(chunk)
# @click.option(
#     "--out",
#     "-o",
#     help="Output directory in which to place the uri and its relative dependencies",
#     type=click.Path(exists=False, path_type=Path, file_okay=False, dir_okay=True),
#     default="./out",
#     show_default=True,
#     metavar="OUT_DIR",
# )
# @click.argument(
#     "csvw_url",
#     type=click.STRING,
#     metavar="CSVW_METADATA_URL",
# )
def _pull():
    """
    Pull a uri and all relative dependencies to the local filesystem.
    """
    urireplacement.replace()

