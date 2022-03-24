"""
Metadata Processor
------------------

Provides functionality for validating and detecting input metadata.json file.
"""
import logging
from pathlib import Path

from rdflib import Graph

from csvcubed.utils.csvw import load_table_schema_file_to_graph
from csvcubed.cli.inspect.inspectsparqlmanager import (
    select_csvw_table_schema_file_dependencies,
)
from csvcubed.models.csvcubedexception import (
    FailedToLoadTableSchemaIntoRDFGraphException,
    FailedToParseJSONldtoRDFGraphException,
)

_logger = logging.getLogger(__name__)


class MetadataProcessor:
    """
    This class handles the loading of metadata jsons to RDFLib Graphs.
    """

    def __init__(self, csvw_metadata_file_path: Path):
        self.csvw_metadata_file_path = csvw_metadata_file_path

    @staticmethod
    def _load_table_schema_dependencies_into_rdf_graph(graph: Graph) -> None:
        """
        Loads the table schemas into rdf graph.

        Member of :class:`./MetadataProcessor`.

        :return: `Graph` - RDFLib Graph of CSV-W metadata json.
        """
        dependencies_result = select_csvw_table_schema_file_dependencies(graph)

        for table_schema_file in dependencies_result.table_schema_file_dependencies:
            try:
                _logger.debug(
                    "Loading dependent file containing table schema %s into RDF graph.",
                    table_schema_file,
                )

                load_table_schema_file_to_graph(table_schema_file, graph)
            except Exception as ex:
                raise FailedToLoadTableSchemaIntoRDFGraphException(
                    table_schema_file=table_schema_file
                ) from ex

        _logger.info(
            "Successfully loaded %d table schemas into the rdf graph.",
            len(dependencies_result.table_schema_file_dependencies),
        )

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

            self._load_table_schema_dependencies_into_rdf_graph(csvw_metadata_rdf_graph)
            return csvw_metadata_rdf_graph
        except Exception as ex:
            raise FailedToParseJSONldtoRDFGraphException(
                csvw_metadata_file_path=csvw_metadata_file_path
            ) from ex
