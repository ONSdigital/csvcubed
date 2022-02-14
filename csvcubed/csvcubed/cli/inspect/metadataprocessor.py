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
    This class handles the conversion/serialisation of metadata jsons to RDF.
    """

    def serialise_to_rdf(self, metadata_json: Path, type: MetadataType) -> Graph:
        """
        Serialises given metadata json to RDF.

        Member of :class:`./MetadataProcessor`.

        :return: `Graph` - RDF Graph of CSV-W metadata.
        """

        """TODO: Convert Metadata json to RDF"""
        graph = Graph()
        return graph
