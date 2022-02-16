"""
Metadata Input Handler
----------------------

Provides functionality for validating the input metadata.json and detecting its type (i.e. DataCube, CodeList or other) file.
"""

import logging

from enum import Enum
from pathlib import Path
from typing import Tuple
from csvcubed.utils.sparql import ask

from rdflib import Graph

_logger = logging.getLogger(__name__)


class CSVWType(Enum):
    """
    The type of metadata file.
    """

    QbDataSet = 0
    """ The metadata file is of type data cube dataset. """

    CodeList = 1
    """ The metadata file is of type code list/concept scheme. """

    Other = 2
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

    # Below code is duplicated from csvcubed pmd package. In the future, we would need to abstract away this to a shared utils project.
    def _detect_type(self) -> CSVWType:
        """
        Detects the type of metadata file.

        Member of :class:`./MetadataValidator`.

        :return: `CSVWMetadataType` - The `CSVWMetadataType` provides the type of metadata file.
        """
        is_code_list = ask(
            """
                ASK 
                WHERE {
                    ?conceptScheme a <http://www.w3.org/2004/02/skos/core#ConceptScheme>.
                }
            """,
            self.csvw_metadata_rdf_graph,
        )

        is_qb_dataset = ask(
            """
                ASK 
                WHERE {
                    ?qbDataSet a <http://purl.org/linked-data/cube#DataSet>.
                }
            """,
            self.csvw_metadata_rdf_graph,
        )

        if is_qb_dataset:
            return CSVWType.QbDataSet
        elif is_code_list:
            return CSVWType.CodeList
        else:
            return CSVWType.Other
