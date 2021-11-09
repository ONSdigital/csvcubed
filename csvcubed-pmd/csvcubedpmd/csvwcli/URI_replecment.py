import click

@click.command()
@click.argument('src', envvar='SRC', type=click.File('turtle_test_file.ttl'))
def echo(src):
    """Print value of SRC environment variable."""
    click.echo(src.read())