import click
#csvcubed_pmd =  __import__('csvcubed-pmd')
#from csvcubed_pmd.tests import turle_test_file

def replace():
    pass

@click.command()
@click.argument('turtle_test_file.ttl', type=click.Path(exists=True))
def touch(filename):
    """Print FILENAME if the file exists."""
    click.echo(click.format_filename(filename))

class click.File(mode='r', encoding=None, errors='strict', lazy=None, atomic=False)
@click.command()
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def inout(input, output):
    """Copy contents of INPUT to OUTPUT."""
    while True:
        chunk = input.read(1024)
        if not chunk:
            break
        output.write(chunk)