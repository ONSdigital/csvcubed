"""
Metadata Input Handler
----------------------

Provides functionality for validating the input metadata.json and detecting its type (i.e. DataCube, CodeList or other) file.
"""

from enum import Enum, auto
from typing import Tuple

from rdflib import Graph

from csvcubed.cli.inspect.inspectsparqlmanager import (
    ask_is_csvw_code_list,
    ask_is_csvw_qb_dataset,
)


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


class MetadataValidator:
    """
    This class validates the input metadata files and detects the metadata type.
    """

    def __init__(self, csvw_metadata_rdf_graph: Graph):
        self.csvw_metadata_rdf_graph = csvw_metadata_rdf_graph

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

        if ask_is_csvw_code_list(self.csvw_metadata_rdf_graph):
            return CSVWType.CodeList
        elif ask_is_csvw_qb_dataset(self.csvw_metadata_rdf_graph):
            return CSVWType.QbDataSet
        else:
            return CSVWType.Other
