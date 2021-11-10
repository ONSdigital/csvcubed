"""
PMD Tools CLI
-------------
"""
import click

from csvcubedpmd.csvwcli import URI_replacement__init__

entry_point2 = click.Group(
    commands=[URI_replacement__init__.uri_group],
    help="find and replece URIs in ttl files.",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
