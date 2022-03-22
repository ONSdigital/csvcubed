"""
Metadata Processor
------------------

Provides functionality for validating and detecting input metadata.json file.
"""

import os
import logging
from pathlib import Path
from typing import List

from rdflib import Graph

from csvcubed.cli.inspect.inspectsparqlmanager import select_csvw_table_schemas

_logger = logging.getLogger(__name__)


class MetadataProcessor:
    """
    This class handles the loading of metadata jsons to RDFLib Graphs.
    """

    def __init__(self, csvw_metadata_file_path: Path):
        self.csvw_metadata_file_path = csvw_metadata_file_path

    def _load_table_schemas_into_rdf_graph(
        self, graph: Graph, table_schemas: List[str], csvw_path: Path
    ) -> Graph:
        """
        Loads the table schemas into rdf graph.

        Member of :class:`./MetadataProcessor`.

        :return: `Graph` - RDFLib Graph of CSV-W metadata json.
        """
        for table_schema in table_schemas:
            table_schema_path: str = os.path.relpath(
                table_schema,
                csvw_path.parent,
            )

            try:
                graph.parse(table_schema_path)
            except Exception as ex:
                raise Exception(
                    "An error occured while loading table schema json into rdf graph"
                ) from ex

        _logger.info(
            f"Successfully loaded {len(table_schemas)} table schemas into the rdf graph."
        )
        return graph

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

            # TODO: The sparql query for getting table schemas return wrong results.
            #result = select_csvw_table_schemas(csvw_metadata_rdf_graph)
            #print(result)
            # if len(result.table_schemas_need_loading) > 0:
            #     csvw_metadata_rdf_graph = self._load_table_schemas_into_rdf_graph(
            #         csvw_metadata_rdf_graph,
            #         result.table_schemas_need_loading,
            #         csvw_metadata_file_path,
            #     )
            return csvw_metadata_rdf_graph
        except Exception as ex:
            raise Exception(
                "An error occured while parsing csvw json-ld to rdf graph"
            ) from ex
