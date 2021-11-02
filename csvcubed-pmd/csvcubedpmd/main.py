"""
PMD Tools CLI
-------------
"""
import click


from csvcubedpmd import codelistcli, csvwcli

entry_point = click.Group(
    commands=[codelistcli.codelist_group, csvwcli.csvw_group],
    help="pmdutils - Utils for helping convert CSV-Ws to PMD-compatible RDF.",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
