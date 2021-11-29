"""
PMD Tools CLI
-------------
"""
import click

from csvcubedpmd import csvwcli, dcatcli


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


_suppress_rdf_lib_json_ld_import_warning()

entry_point = click.Group(
    commands=[csvwcli.csvw_group, dcatcli.dcat_group],
    help="pmdutils - Utils for helping convert CSV-Ws to PMD-compatible RDF.",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
