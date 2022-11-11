"""
Metadata Input Handler
----------------------

Provides functionality for validating the input metadata.json and detecting its type (i.e. DataCube, CodeList or other) file.
"""
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional, Tuple

import rdflib
from csvcubed.models.sparqlresults import IsPivotedShapeMeasureResult

from csvcubed.utils.sparql_handler.sparqlmanager import (
    ask_is_csvw_code_list,
    ask_is_csvw_qb_dataset,
)
from csvcubed.utils.sparql_handler.sparql import path_to_file_uri_for_rdflib
from csvcubed.models.cube.cube_shape import CubeShape


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

    def detect_type_and_shape(self, is_pivoted_measures: List[IsPivotedShapeMeasureResult]) -> Tuple[CSVWType, Optional[CubeShape]]:
        """
        Detects the type and shape of the csvw.
        """
        csvw_type = self._detect_type()
        cube_shape = self._detect_shape(is_pivoted_measures) if csvw_type == CSVWType.QbDataSet else None

        return (csvw_type, cube_shape)

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
            raise TypeError(
                "The input metadata is invalid as it is not a data cube or a code list."
            )

    def _detect_shape(self, is_pivoted_measures: List[IsPivotedShapeMeasureResult]) -> CubeShape:
        """
        Given a metadata validator as input, returns the shape of the cube that metadata describes (Pivoted or Standard).
        """
        all_pivoted = True
        all_standard_shape = True
        for measure in is_pivoted_measures:
            all_pivoted = all_pivoted and measure.is_pivoted_shape
            all_standard_shape = all_standard_shape and not measure.is_pivoted_shape

        if all_pivoted:
            return CubeShape.Pivoted
        elif all_standard_shape:
            return CubeShape.Standard
        else:
            raise TypeError(
                "The input metadata is invalid as the shape of the cube it represents is not supported. More specifically, the input contains some observation values that are pivoted and some are not pivoted."
            )
