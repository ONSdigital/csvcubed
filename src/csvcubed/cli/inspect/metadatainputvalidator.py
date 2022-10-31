"""
Metadata Input Handler
----------------------

Provides functionality for validating the input metadata.json and detecting its type (i.e. DataCube, CodeList or other) file.
"""
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import List, Tuple

import rdflib
from csvcubed.models.sparqlresults import IsPivotedShapeMeasureResult

from csvcubed.utils.sparql_handler.sparqlmanager import (
    CSVWShape,
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
    is_pivoted_measures: List[IsPivotedShapeMeasureResult]

    def validate_csvw(self) -> Tuple[bool, CSVWType, CSVWShape]:
        """
        Detects the validity, type and shape of the csvw.
        """
        validity = CSVWType.QbDataSet or csvw_type == CSVWType.CodeList
        csvw_type = self._detect_type()
        csvw_shape = self._detect_shape()

        return (
            validity,
            csvw_type,
            csvw_shape
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
    
    def _detect_shape(self) -> CSVWShape:
        """
        TODO: Description
        """

        # Csvw is a pivoted shape csvw, if all the measures are pivoted shape
        # Csvw is a standard shape csvw, if all the measures are NOT pivoted shape
        # Otherwise, it is not a supported csvw, hence throw a user-friendly error with inspect error types

        #self.is_pivoted_measures[0].is_pivoted_shape
        
        return CSVWShape.Standard
