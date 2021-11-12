import click

def _line_check(line: str) -> bool:
    """
    Returns true if line has no file:/ in it
    """
    return not "file:/" in line


def _line_replace(line: str, values: tuple[tuple[str, str]]) -> str:
    """
    Replaces given value pairs in line, returns result
    """
    print(f"Original line: {line}")
    for find, replace in values:
        print(f"replacing [{find}] with [{replace}]")
        line = line.replace(find, replace)
    print(f"New line: {line}")
    # for paireduris in values:
    #     whichuri = values[paireduris]
    #     if whichuri[0] in line:
    #         line.replace(whichuri[0],whichuri[1])
    #         print(line)

                
    return line

def _replace(input: click.File, output: click.File, values: tuple[tuple[str, str]]) -> None:
    """
    Docstring goes here
    """

    "Get character encoding type as a variable"
    while True:
        chunk = input.readline()
        line = (input.readline()).decode()
        "Add reading the line and decoding as one statement - it's no longer a chunk, maybe try would work here?"
        if not line:
            break
        _line_replace(line,values)
        "encode it back to that bytestream"
        line = line.encode()
        output.write(line)
        print(line)
        print(type(values))
    for value in values:
        print(f"Replace [{value[0]}] with [{value[1]}]")
