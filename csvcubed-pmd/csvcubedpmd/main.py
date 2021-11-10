"""
PMD Tools CLI
-------------
"""
import click


from csvcubedpmd import csvwcli
from csvcubedpmd.csvwcli import URI_replacement__init__

entry_point = click.Group(
    commands=[csvwcli.csvw_group],
    help="pmdutils - Utils for helping convert CSV-Ws to PMD-compatible RDF.",
    context_settings=dict(help_option_names=["-h", "--help"]),
)

entry_point2 = click.Group(
    commands=[URI_replacement__init__.uri_group],
    help="find and replece URIs in ttl files.",
    context_settings=dict(help_option_names=["-h", "--help"]),
)