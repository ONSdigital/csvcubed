"""
REPLACE URI
-----------

Functionality to read in ttl files, to find and replace uris.
"""
from typing import Optional, Union
import click
import sys
import os

from chardet.universaldetector import UniversalDetector
import logging

from click.types import Path


def _file_in_line(line: str) -> bool:
    """
    Returns true if line has file:/ in it
    """
    return "file:/" in line


def _line_replace(line: str, values: list[tuple[str, str]]) -> str:
    """
    Replaces given value pairs in line, returns result
    """

    logging.debug(f"Original line: {line}")
    for find, replace in values:
        logging.debug(f"replacing [{find}] with [{replace}]")
        line = line.replace(find, replace)
    logging.debug(f"New line: {line}")

    return line


def _chardet(input: click.Path) -> str:
    """
    Detects the encoding type of a file and returns result
    """
    detector = UniversalDetector()
    with open(str(input), "rb") as inputfile:
        for line in inputfile.readlines():
            logging.debug(line)
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        logging.info(detector.result)
        encodingtype = detector.result["encoding"]

    if encodingtype is None:
        encodingtype = "UTF-8"

    return encodingtype


def _replace(
    input: click.Path, output: click.Path, values: list[tuple[str, str]], force: bool
) -> None:
    """
    Streams in a ttl file line by line, finds and replaces all instances of specified URIs begining with 'file:/' with 'http://...'
    """
    logging.basicConfig(level=logging.INFO)

    # Get character encoding type as a variable
    encodingtype = _chardet(input)
    logging.info(encodingtype)

    # If one pair of uri values are entered into the command line
    for (find, replacement) in values:
        logging.info(f"Replacing {find} with {replacement}")

    # Otherwise if multiple pair of uri values where entered into the command line
    with open(str(input), "rb") as inputfile, open(str(output), "wb") as outputfile:
        for index, line in enumerate(inputfile, 1):

            line = line.decode(encodingtype)
            # logging.debug(index, line)

            line = _line_replace(line, values)
            if _file_in_line(line):
                logging.warning(
                    f"remaining 'file:/' URIs found on line {index}: {line}"
                )
                if not force:
                    # delete output file
                    os.remove(str(output))
                    sys.exit(1)

            outputfile.write(line.encode(encodingtype))
