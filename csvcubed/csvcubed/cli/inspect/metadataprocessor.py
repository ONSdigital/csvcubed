"""
Metadata Processor
------------------

Provides functionality for validating and detecting input metadata.json file.
"""

import os
import logging
from pathlib import Path

from rdflib import Graph

from csvcubed.cli.inspect.inspectsparqlmanager import select_csvw_table_schema

_logger = logging.getLogger(__name__)


class MetadataProcessor:
    """
    This class handles the loading of metadata jsons to RDFLib Graphs.
    """

    def __init__(self, csvw_metadata_file_path: Path):
        self.csvw_metadata_file_path = csvw_metadata_file_path

    def _load_table_schema_into_rdf_graph(
        self, graph: Graph, table_schema_name: str, csvw_path: Path
    ) -> Graph:
        """
        Loads the table schema into rdf graph, if the table schema is not defined in the csvw json-ld.
        """
        table_schema_path: str = os.path.relpath(
            table_schema_name,
            csvw_path.parent,
        )

        try:
            graph.parse(table_schema_path)
            _logger.info("Successfully loaded external table schema into rdf graph.")
            return graph
        except Exception as ex:
            raise Exception(
                "An error occured while loading table schema json into rdf graph"
            ) from ex

    def load_json_ld_to_rdflib_graph(self) -> Graph:
        """
        Loads CSV-W metadata json-ld to rdflib graph

        Member of :class:`./MetadataProcessor`.

        :return: `Graph` - RDFLib Graph of CSV-W metadata json.
        """
        csvw_metadata_file_path = self.csvw_metadata_file_path.absolute()
        csvw_metadata_rdf_graph = Graph()

        try:
            csvw_metadata_rdf_graph.parse(csvw_metadata_file_path, format="json-ld")
            _logger.info("Successfully parsed csvw json-ld to rdf graph.")

            # result = select_csvw_table_schema(csvw_metadata_rdf_graph)
            # if not result.table_schema_is_defined:
            #     csvw_metadata_rdf_graph = self._load_table_schema_into_rdf_graph(
            #         csvw_metadata_rdf_graph,
            #         result.table_schema,
            #         csvw_metadata_file_path,
            #     )
            return csvw_metadata_rdf_graph
        except Exception as ex:
            raise Exception(
                "An error occured while parsing csvw json-ld to rdf graph"
            ) from ex
