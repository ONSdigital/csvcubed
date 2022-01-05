from pathlib import Path
import click

from csvcubedpmd.csvwcli import pull, findwhere

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


@csvw_group.command("find-where")
@click.option(
    "--inside",
    "-i",
    help="Directory in which to search for CSV-W Metadata Files",
    type=click.Path(exists=True, path_type=Path, file_okay=False, dir_okay=True),
    default=".",
    show_default=True,
    metavar="SEARCH_DIR",
)
@click.option(
    "--negate", "-n", help="Negate the result of running the ASK query.", is_flag=True
)
@click.argument(
    "ask_query",
    type=click.STRING,
    metavar="ASK_QUERY",
)
def _find_where(inside: Path, negate: bool, ask_query: str):
    """
    Find all CSV-W metadata files within a given directory which match an ASK query.
    """
    findwhere.find_where(inside, ask_query, negate)
