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


@uri_group.command('replace')
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

