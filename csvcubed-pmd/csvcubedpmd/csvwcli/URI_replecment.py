import click

@click.command()
@click.argument('src', envvar='SRC', type=click.File('r'))
def echo(src):
    """Print value of SRC environment variable."""
    click.echo(src.read(turtle_test_file.ttl))