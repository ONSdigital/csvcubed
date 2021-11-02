"""
PMD Tools CLI
-------------
"""
import click


from csvcubedpmd import codelist, csvw

entry_point = click.Group(
    commands=[codelist.codelist_group, csvw.csvw_group],
    help="pmdutils - Utils for helping convert CSV-Ws to PMD-compatible RDF.",
    context_settings=dict(help_option_names=["-h", "--help"]),
)
