"""
Metadata Input Handler
----------------------

Provides functionality for validating the input metadata.json and detecting its type (i.e. DataCube, CodeList or other) file.
"""
from dataclasses import dataclass
from pathlib import Path

import rdflib

from csvcubed.models.csvwtype import CSVWType
from csvcubed.utils.sparql_handler.sparql import path_to_file_uri_for_rdflib
from csvcubed.utils.sparql_handler.sparqlquerymanager import (
    ask_is_csvw_code_list,
    ask_is_csvw_qb_dataset,
)


@dataclass
class MetadataValidator:
    """
    This class validates the input metadata files and detects the metadata type.
    """

    csvw_metadata_rdf_graph: rdflib.ConjunctiveGraph
    csvw_metadata_json_path: Path

    def detect_csvw_type(self) -> CSVWType:
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
