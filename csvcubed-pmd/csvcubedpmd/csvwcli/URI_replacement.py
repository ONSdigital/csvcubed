import click

@click.command()
@click.argument('turtle_test_file.ttl')
def touch(turtle_test_file.ttl):
    """Print turtle_test_file.ttl."""
    click.echo(turtle_test_file.ttl)

