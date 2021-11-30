from pathlib import Path
import click

from .pmdify import pmdify_dcat


@click.group("dcat")
def dcat_group():
    """
    Work with DCAT metadata.
    """
    pass


@dcat_group.command("pmdify")
@click.argument(
    "csvw_metadata_file",
    type=click.Path(exists=True, path_type=Path, file_okay=True, dir_okay=False),
    metavar="CSVW_METADATA_FILE",
)
@click.argument(
    "base_uri",
    type=str,
    metavar="BASE_URI",
)
@click.argument(
    "data_graph_uri",
    type=str,
    metavar="DATA_GRAPH_URI",
)
@click.argument(
    "catalog_metadata_graph_uri",
    type=str,
    metavar="CATALOG_METADATA_GRAPH_URI",
)
def _pmdify(
    csvw_metadata_file: Path,
    base_uri: str,
    data_graph_uri: str,
    catalog_metadata_graph_uri: str,
) -> None:
    """
    Given a local CSV-W metadata.json file, re-work the DCATv2 metadata such that it ends up in the format required
    for PMD.

    Removes the expected DCAT metadata from the CSV-W metadata.json file and outputs a new N-Quads file containing
    PMDCAT metadata at <CSVW_METADATA_FILE>.nq
    """
    pmdify_dcat(
        csvw_metadata_file, base_uri, data_graph_uri, catalog_metadata_graph_uri
    )
