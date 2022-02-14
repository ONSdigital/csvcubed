"""
Metadata Processor
---------------------------

Provides functionality for validating and detecting input metadata.json file.
"""

import logging

from pathlib import Path
from csvcubed.cli.inspect.metadatainputhandler import MetadataType
from rdflib import Graph

_logger = logging.getLogger(__name__)


class MetadataProcessor:
    """
    This class handles the loading of metadata jsons to RDFLib Graphs.
    """

    def load_json_ld_to_rdflib_graph(
        self, metadata_json: Path, type: MetadataType
    ) -> Graph:
        """
        Loads metadata json to RDFLib Graph

        Member of :class:`./MetadataProcessor`.

        :return: `Graph` - RDFLib Graph of CSV-W metadata json.
        """

        """TODO: Convert Metadata json to RDFLib Graph"""
        graph = Graph()
        return graph
