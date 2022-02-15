"""
Metadata Input Handler
----------------------

Provides functionality for validating the input metadata.json and detecting its type (i.e. DataCube, CodeList or other) file.
"""

import logging

from enum import Enum
from pathlib import Path
from typing import Tuple

from rdflib import Graph

_logger = logging.getLogger(__name__)


class MetadataType(Enum):
    """
    The type of metadata file.
    """

    DataCube = 0
    """ The metadata file is of type data cube. """

    CodeList = 1
    """ The metadata file is of type code list. """

    Other = 2
    """ The metadata file is not of types data cube and code list. This type of metadata files is currently not supported by the `csvcubed inspect`."""


class MetadataInputHandler:
    """
    This class validates the input metadata files and detects the metadata type.
    """

    def __init__(self, csvw_metadata_rdf_graph: Graph):
        self.csvw_metadata_rdf_graph = csvw_metadata_rdf_graph

    def validate_input(self) -> Tuple[bool, MetadataType]:
        """
        Detects the validity and type of metadata file.

        Member of :class:`./MetadataInputHandler`.

        :return: `Tuple[bool, MetadataType]` - the boolean shows whether the metadata file is valid (`True`) or invalid (`False`). The `MetadataType` provides the type of metadata file.
        """
        metadata_type = self._detect_input_type()
        return (
            metadata_type == MetadataType.DataCube
            or metadata_type == MetadataType.CodeList,
            metadata_type,
        )

    def _detect_input_type(self) -> MetadataType:
        """
        Detects the type of metadata file.

        Member of :class:`./MetadataInputHandler`.

        :return: `MetadataType` - The `MetadataType` provides the type of metadata file.
        """

        """TODO: Detect metadata input type (i.e. data cube, code list or other)"""
        input_type = MetadataType.CodeList
        return input_type
