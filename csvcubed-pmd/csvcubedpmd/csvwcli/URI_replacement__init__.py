from pathlib import Path
from typing import Any
import click

import csvcubedpmd.csvwcli.URI_replecment as URI_replecment

click.group("uri")
def uri_group():
    """
    Work with URIs.
    """
    pass


#@uri_group.command()
@click.option(
    "--out",
    "-o",
    help="Output directory in which to place the uri and its relative dependencies",
    type=click.Path(exists=False, path_type=Path, file_okay=False, dir_okay=True),
    default="./out",
    show_default=True,
    metavar="OUT_DIR",
)
@click.argument(
    "csvw_url",
    type=click.STRING,
    metavar="CSVW_METADATA_URL",
)
def _pull(out: Path, csvw_url: str):
    """
    Pull a uri and all relative dependencies to the local filesystem.
    """
    pull.pull(csvw_url, out.absolute())
