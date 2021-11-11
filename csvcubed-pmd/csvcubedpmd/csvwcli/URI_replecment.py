import click

def replace():
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