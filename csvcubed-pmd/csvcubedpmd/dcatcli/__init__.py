from pathlib import Path
import click

from .pmdify import pmdify_dcat


@click.group("dcat")
def dcat_group():
    """
    Work with CSV-Ws.
    """
    pass


@dcat_group.command("pmdify")
@click.argument(
    "csvw_metadata_file",
    type=click.Path(exists=True, path_type=Path, file_okay=True, dir_okay=False),
    metavar="CSVW_METADATA_FILE",
)
def _pmdify(csvw_metadata_file: Path) -> None:
    """
    Given a local CSV-W metadata file, re-work the DCATv2 metadata such that it ends up in the format required for PMD
    """
    pmdify_dcat(csvw_metadata_file)
