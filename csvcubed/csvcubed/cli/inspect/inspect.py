"""
Inspect Command
---------------

Output CSV-W metadata in a user-friendly format to the CLI for validation.
"""

import logging
from pathlib import Path
from typing import Tuple

from rdflib import Graph

from csvcubed.cli.inspect.metadatainputvalidator import (
    CSVWType,
    MetadataValidator,
)
from csvcubed.cli.inspect.metadataprinter import MetadataPrinter
from csvcubed.cli.inspect.metadataprocessor import MetadataProcessor

_logger = logging.getLogger(__name__)


def inspect(csvw_metadata_json_path: Path) -> None:
    """
    Command for validating CSV-W metadata files through the CLI.

    Member of :file:`./inspect.py`

    :return: `None`
    """
    metadata_processor = MetadataProcessor(csvw_metadata_json_path)
    csvw_metadata_rdf_graph = metadata_processor.load_json_ld_to_rdflib_graph()

    assert csvw_metadata_rdf_graph is not None

    csvw_metadata_rdf_validator = MetadataValidator(csvw_metadata_rdf_graph)
    (
        valid_csvw_metadata,
        csvw_type,
    ) = csvw_metadata_rdf_validator.validate_and_detect_type()

    if valid_csvw_metadata:
        (
            type_printable,
            metadata_info_printable,
            dsd_info_printable,
            codelist_info_printable,
            headtail_printable,
            valcount_printable,
        ) = _generate_printables(csvw_type, csvw_metadata_rdf_graph)

        _logger.info("Type: %s", type_printable)
        _logger.info("Description: %s", metadata_info_printable)
        _logger.info("Data Structure Definition: %s", dsd_info_printable)
    else:
        _logger.error(
            "This is an unsupported csv-w! Supported types are `data cube` and `code list`."
        )


def _generate_printables(
    csvw_type: CSVWType, csvw_metadata_rdf_graph: Graph
) -> Tuple[str, str, str, str, str, str]:
    """
    Generates printables of type, metadata, dsd, code list, head/tail and value count information.

    Member of :file:`./inspect.py`

    :return: `Tuple[str, str, str, str, str]` - printables of metadata information.
    """
    metadata_printer = MetadataPrinter(csvw_metadata_rdf_graph, csvw_type)

    return (
        metadata_printer.gen_type_info_printable(),
        metadata_printer.gen_metadata_info_printable(),
        metadata_printer.gen_dsd_info_printable(),
        metadata_printer.gen_codelist_info_printable(),
        metadata_printer.gen_headtail_printable(),
        metadata_printer.gen_valcount_printable(),
    )
