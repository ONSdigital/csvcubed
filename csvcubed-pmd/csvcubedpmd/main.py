"""
PMD Tools CLI
-------------
"""
import click

from csvcubedpmd import csvwcli, dcatcli, urireplacement

entry_point = click.Group(
    commands=[csvwcli.csvw_group, dcatcli.dcat_group, urireplacement.uri_group],
    help="pmdutils - Utils for helping convert CSV-Ws to PMD-compatible RDF.",
    context_settings=dict(help_option_names=["-h", "--help"]),
)