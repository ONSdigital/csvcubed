import click

# import urllib.request
from chardet.universaldetector import UniversalDetector
import logging

logging.basicConfig(level=logging.INFO)


def _file_in_line(line: str) -> bool:
    """
    Returns true if line has file:/ in it
    """
    return "file:/" in line


def _line_replace(line: str, values: tuple[tuple[str, str]]) -> str:
    """
    Replaces given value pairs in line, returns result
    """

    logging.debug(f"Original line: {line}")
    if type(values[0]) == str:
        logging.debug(f"replacing [{values[0]}] with [{values[1]}]")
        line = line.replace(values[0], values[1])
    else:
        for find, replace in values:
            logging.debug(f"replacing [{find}] with [{replace}]")
            line = line.replace(find, replace)
    logging.debug(f"New line: {line}")

    return line


def _chardet(input: click.Path):
    detector = UniversalDetector()
    with open(input, "rb") as inputfile:
        for line in inputfile.readlines():
            logging.debug(line)
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        logging.info(detector.result)
        encodingtype = detector.result["encoding"]

    return encodingtype


def _replace(
    input: click.Path, output: click.Path, values: tuple[tuple[str, str]], force: bool
) -> None:
    """
    Docstring goes here
    """

    "Get character encoding type as a variable"
    encodingtype = _chardet(input)
    logging.info(encodingtype)

    # Show people what you're doing if you want to see it
    for value in values:
        logging.info(f"Replace [{value[0]}] with [{value[1]}]")

    with open(input, "rb") as inputfile:
        with open(output, "wb") as outputfile:
            for index, line in enumerate(inputfile, 1):

                line = line.decode(encodingtype)
                logging.debug(index, line)
                "Add reading the line and decoding as one statement - it's no longer a chunk, maybe try would work here?"

                line = _line_replace(line, values)
                if _file_in_line(line):
                    logging.warning(
                        f"remiaining 'file:/' URIs found on line {index}: {line}"
                    )
                    if force:
                        logging.debug("CLI program stop running")
                        break
                else:
                    logging.debug(f'"file:/" not found on line {index}')
                outputfile.write(line.encode(encodingtype))
                logging.debug(line)
                logging.debug(type(values))
