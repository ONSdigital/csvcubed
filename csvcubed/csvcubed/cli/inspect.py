"""
Inspect Command
---------------

Output CSV-W metadata in a user-friendly format to the CLI for validation.
"""

import logging

from pathlib import Path
from typing import Tuple

from csvcubed.cli.inspect_cli.metadatainputhandler import (
    MetadataInputHandler,
    MetadataType,
)
from csvcubed.cli.inspect_cli.metadataprinter import MetadataPrinter
from csvcubed.cli.inspect_cli.metadataprocessor import MetadataProcessor
from rdflib import Graph

_logger = logging.getLogger(__name__)


def inspect(metadata_json: Path) -> None:
    """
    Command for validating CSV-W metadata files through the CLI.
    
    Member of :file:`./inspect.py`

    :return: `None`
    """
    input_handler = MetadataInputHandler(metadata_json)
    metadata_processor = MetadataProcessor()

    valid_input, input_type = input_handler.validate_input()
    if valid_input:
        metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph(metadata_json, input_type)
        """TODO: Output below printables to the CLI"""
        (
            type_printable,
            metadata_info_printable,
            dsd_info_printable,
            codelist_info_printable,
            headtail_printable,
            valcount_printable,
        ) = _generate_printables(input_type, metadata_rdf_graph)

    else:
        _logger.debug("Display unsupported input error message to the user")


def _generate_printables(
    metadata_type: MetadataType, metadata_rdf_graph: Graph
) -> Tuple[str, str, str, str, str, str]:
    """
    Generates printables of type, metadata, dsd, code list, head/tail and value count information.

    Member of :file:`./inspect.py`

    :return: `Tuple[str, str, str, str, str]` - printables of metadata information.
    """
    metadata_printer = MetadataPrinter(metadata_rdf_graph)

    return (
        metadata_printer.gen_type_info_printable(metadata_type),
        metadata_printer.gen_metadata_info_printable(),
        metadata_printer.gen_dsd_info_printable(),
        metadata_printer.gen_codelist_info_printable(),
        metadata_printer.gen_headtail_printable(),
        metadata_printer.gen_valcount_printable(),
    )
