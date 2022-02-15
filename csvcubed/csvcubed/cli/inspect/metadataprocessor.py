"""
Metadata Processor
---------------------------

Provides functionality for validating and detecting input metadata.json file.
"""

import json
import logging

from pathlib import Path
from rdflib import Graph, URIRef

_TEMP_PREFIX_URI = URIRef("http://temporary")

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
        csvw_rdf_graph = Graph(base=_TEMP_PREFIX_URI)

        try:
            with open(csvw_metadata_file_path, "r") as f:
                csvw_file_contents: str = f.read()
                _logger.info(
                    f"Successfully read content from %s",
                    self.csvw_metadata_file_path,
                )
        except Exception:
            _logger.exception(f"An error occured while reading csvw file content")
            return None

        try:
            csvw_rdf_graph.parse(
                data=csvw_file_contents, publicID=_TEMP_PREFIX_URI, format="json-ld"
            )
            _logger.info("Successfully parsed csvw json-ld to rdf graph")
            return csvw_rdf_graph
        except Exception:
            _logger.exception(
                f"An error occured while parsing csvw json-ld to rdf graph"
            )
            return None
