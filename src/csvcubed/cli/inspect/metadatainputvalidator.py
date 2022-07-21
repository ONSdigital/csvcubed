"""
Metadata Input Handler
----------------------

Provides functionality for validating the input metadata.json and detecting its type (i.e. DataCube, CodeList or other) file.
"""
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Tuple

import rdflib

from csvcubed.utils.sparql_handler.sparqlmanager import (
    ask_is_csvw_code_list,
    ask_is_csvw_qb_dataset,
)
from csvcubed.utils.sparql_handler.sparql import path_to_file_uri_for_rdflib


class CSVWType(Enum):
    """
    The type of metadata file.
    """

    QbDataSet = auto()
    """ The metadata file is of type data cube dataset. """

    CodeList = auto()
    """ The metadata file is of type code list/concept scheme. """

    Other = auto()
    """ The metadata file is not of types data cube and code list. This type of metadata files is not supported."""


@dataclass
class MetadataValidator:
    """
    This class validates the input metadata files and detects the metadata type.
    """

    csvw_metadata_rdf_graph: rdflib.ConjunctiveGraph
    csvw_metadata_json_path: Path

    def validate_and_detect_type(self) -> Tuple[bool, CSVWType]:
        """
        Detects the validity and type of metadata file.

        Member of :class:`./MetadataValidator`.

        :return: `Tuple[bool, MetadataType]` - the boolean shows whether the metadata file is valid (`True`) or invalid (`False`). The `MetadataType` provides the type of metadata file.
        """
        metadata_type = self._detect_type()
        return (
            metadata_type == CSVWType.QbDataSet or metadata_type == CSVWType.CodeList,
            metadata_type,
        )

    def _detect_type(self) -> CSVWType:
        """
        Detects the type of metadata file.

        Member of :class:`./MetadataValidator`.

        :return: `CSVWType` - The `CSVWType` provides the type of metadata file.
        """

        primary_graph_identifier = path_to_file_uri_for_rdflib(
            self.csvw_metadata_json_path
        )
        primary_graph = self.csvw_metadata_rdf_graph.get_context(
            primary_graph_identifier
        )

        if ask_is_csvw_code_list(primary_graph):
            return CSVWType.CodeList
        elif ask_is_csvw_qb_dataset(primary_graph):
            return CSVWType.QbDataSet
        else:
            return CSVWType.Other
