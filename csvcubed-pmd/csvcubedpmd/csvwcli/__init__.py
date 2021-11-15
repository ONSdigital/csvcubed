from pathlib import Path
import click

import csvcubedpmd.csvwcli.pull as pull


@click.group("csvw")
def csvw_group():
    """
    Work with CSV-Ws.
    """
    pass


@csvw_group.command("pull")
@click.option(
    "--out",
    "-o",
    help="Output directory in which to place the CSV-W and its relative dependencies",
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
    Pull a CSV-W and all relative dependencies to the local filesystem.
    """
    pull.pull(csvw_url, out.absolute())
