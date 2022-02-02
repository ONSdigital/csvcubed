"""
CLI
---
The *Command Line Interface* for :mod:`~gssutils.csvcubedintegration.infojson2csvqb`.
"""
import click
from pathlib import Path
import colorama

from .csvcubedbuild import build


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def entry_point():
    """
    infojson2csvqb - a tool to generate qb-flavoured CSV-W cubes from COGS-style info.json files.
    """
    _suppress_rdf_lib_json_ld_import_warning()
    colorama.init(autoreset=True, wrap=True)


@entry_point.command("build")
@click.option(
    "--config",
    "-c",
    help="Location of the info.json file containing the QB column mapping definitions.",
    type=click.Path(exists=True, path_type=Path, file_okay=True, dir_okay=False),
    required=True,
    metavar="CONFIG_PATH",
)
# @click.option(
#     "--catalog-metadata",
#     "-m",
#     help=(
#         "Location of a JSON file containing the Catalog Metadata for this qube. "
#         "If present, this overrides any configuration found in the info.json."
#     ),
#     type=click.Path(exists=True, path_type=Path, file_okay=True, dir_okay=False),
#     required=False,
#     metavar="CATALOG_METADATA_PATH",
# )
@click.option(
    "--out",
    "-o",
    help="Location of the CSV-W outputs.",
    default="./out",
    show_default=True,
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    metavar="OUT_DIR",
)
@click.option(
    "--fail-when-validation-error/--ignore-validation-errors",
    help="Fail when validation errors occur or ignore validation errors and continue generating a CSV-W.",
    default=True,
    show_default=True,
)
@click.option(
    "--validation-errors-to-file",
    "validation_errors_to_file",
    help="Save validation errors to an `validation-errors.json` file in the output directory.",
    flag_value=True,
    default=False,
    show_default=True,
)
@click.argument(
    "csv", type=click.Path(exists=True, path_type=Path), metavar="TIDY_CSV_PATH"
)
def build_command(
    config: Path,
    catalog_metadata: Path,
    out: Path,
    csv: Path,
    fail_when_validation_error: bool,
    validation_errors_to_file: bool,
):
    """Build a qb-flavoured CSV-W from a tidy CSV."""
    validation_errors_file_out = (
        out / "validation-errors.json" if validation_errors_to_file else None
    )
    build(
        config,
        catalog_metadata,
        out,
        csv,
        fail_when_validation_error,
        validation_errors_file_out,
    )


def _suppress_rdf_lib_json_ld_import_warning():
    """
    Unfortunately, the current version of rdflib-jsonld library issued a warning that they seem to insist users see.
    Here's some hacky code to make sure the user never sees it.
    """
    import io
    import sys

    initial_std_err = sys.stderr
    try:
        sys.stderr = io.StringIO()
        import rdflib_jsonld
    finally:
        sys.stderr = initial_std_err