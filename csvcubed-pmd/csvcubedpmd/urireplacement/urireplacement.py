import click
import urllib.request
from chardet.universaldetector import UniversalDetector
import logging

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
    _line_check(line)
    
    return line

def _chardet(input: click.File):
    detector = UniversalDetector()
    for line in input.readlines():
        detector.feed(line)
        if detector.done: break
    detector.close()
    print(detector.result)
    encodingtype = detector.result['encoding']
    return encodingtype

def _replace(input: click.File, output: click.File, values: tuple[tuple[str, str]]) -> None:
    """
    Docstring goes here
    """
    encodingtype = _chardet(input)
    print(encodingtype)
    
    "Get character encoding type as a variable"
    #while True:
    for index, line in enumerate(input):
        line = (input.readline()).decode(encodingtype)
        "Add reading the line and decoding as one statement - it's no longer a chunk, maybe try would work here?"
        if not line:
            break
        _line_replace(line,values)
        if _line_check(line):
            logging.warning(f"remiaining 'file:/' URIs found on line {index}: {line}")
        "encode it back to that bytestream"
        line = line.encode(encodingtype)
        output.write(line)
        print(line)
        print(type(values))
    for value in values:
        print(f"Replace [{value[0]}] with [{value[1]}]")
