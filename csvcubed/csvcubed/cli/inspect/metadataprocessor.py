"""
Metadata Processor
---------------------------

Provides functionality for validating and detecting input metadata.json file.
"""

import logging
from pathlib import Path

from rdflib import Graph

_logger = logging.getLogger(__name__)


class MetadataProcessor:
    """
    This class handles the loading of metadata jsons to RDFLib Graphs.
    """

    def __init__(self, csvw_metadata_file_path: Path):
        self.csvw_metadata_file_path = csvw_metadata_file_path

    def load_json_ld_to_rdflib_graph(self) -> Graph:
        """
        Loads CSV-W metadata json-ld to rdflib graph

        Member of :class:`./MetadataProcessor`.

        :return: `Graph` - RDFLib Graph of CSV-W metadata json.
        """
        csvw_metadata_file_path = self.csvw_metadata_file_path.absolute()
        csvw_metadata_rdf_graph = Graph()
        
        try:
            csvw_metadata_rdf_graph.load(csvw_metadata_file_path, format="json-ld")
            _logger.info("Successfully parsed csvw json-ld to rdf graph.")
            return csvw_metadata_rdf_graph
        except Exception as ex:
            raise Exception(
                "An error occured while parsing csvw json-ld to rdf graph"
            ) from ex
