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
    FailedToLoadRDFGraphException,
    FailedToLoadTableSchemaIntoRdfGraphException,
    FailedToReadCsvwFileContentException,
    InvalidCsvwFileContentException,
)
from csvcubed.utils.sparql import path_to_file_uri_for_rdflib

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
                raise FailedToLoadTableSchemaIntoRdfGraphException(
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
        csvw_metadata_rdf_graph = Graph()
        csvw_file_content: str
        csvw_metadata_file_path = self.csvw_metadata_file_path.absolute()


        """
        Note: in below, we are loading the content of the csvw file into a variable before calling the RDFLib's parse() function.
        This is an alternative to passing in the path of the csvw file directly to the RDFlib's parse() function. 
        
        The reason for doing this is because when concurrent builds are running in Git or Jenkins pipelines, suffixes such as
        @2, @3 and so on (e.g. "path/to/file/dir_@2", "path/to/file/dir_@3") will be appended to the directory path.
        Since RDFLib uses the Path lib which it then url encodes, these graphs will end up with relative URIs turned into absolute URIs 
        containing parts such as "path/to/file/dir_%40"; this makes it hard to identify the correct location of the underlying file when reading results from RDFlib.
        """

        try:
            with open(
                csvw_metadata_file_path,
                "r",
            ) as f:
                csvw_file_content = f.read()
        except Exception as ex:
            raise FailedToReadCsvwFileContentException(
                csvw_metadata_file_path=self.csvw_metadata_file_path
            ) from ex

        if csvw_file_content is None:
            raise InvalidCsvwFileContentException()

        try:
            csvw_metadata_rdf_graph.parse(
                data=csvw_file_content,
                publicID=path_to_file_uri_for_rdflib(csvw_metadata_file_path),
                format="json-ld",
            )
            _logger.info("Successfully parsed csvw json-ld to rdf graph.")

            self._load_table_schema_dependencies_into_rdf_graph(csvw_metadata_rdf_graph)
            return csvw_metadata_rdf_graph
        except Exception as ex:
            raise FailedToLoadRDFGraphException(self.csvw_metadata_file_path) from ex
