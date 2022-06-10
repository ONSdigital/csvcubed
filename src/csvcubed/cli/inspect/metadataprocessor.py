"""
Metadata Processor
------------------

Provides functionality for validating and detecting input metadata.json file.
"""
import logging
from pathlib import Path
from typing import List, Set

import rdflib
from rdflib.util import guess_format

from csvcubed.models.inspectsparqlresults import MetadataDependenciesResult
from csvcubed.utils.csvw import load_table_schema_file_to_graph
from csvcubed.cli.inspect.inspectsparqlmanager import (
    select_csvw_table_schema_file_dependencies,
    select_metadata_dependencies,
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
    def _load_table_schema_dependencies_into_rdf_graph(
        graph: rdflib.ConjunctiveGraph,
    ) -> None:
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

    def load_json_ld_to_rdflib_graph(self) -> rdflib.ConjunctiveGraph:
        """
        Loads CSV-W metadata json-ld to rdflib graph

        Member of :class:`./MetadataProcessor`.

        :return: `Graph` - RDFLib Graph of CSV-W metadata json.
        """
        csvw_metadata_rdf_graph = rdflib.ConjunctiveGraph()
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
            csvw_metadata_rdf_graph += get_triples_for_file_dependencies(
                csvw_metadata_rdf_graph
            )

            return csvw_metadata_rdf_graph
        except Exception as ex:
            raise FailedToLoadRDFGraphException(self.csvw_metadata_file_path) from ex


def get_triples_for_file_dependencies(
    csvw_metadata_rdf_graph: rdflib.Graph,
) -> rdflib.ConjunctiveGraph:
    """
    Loads all dependent RDF metadata files, along with transitive dependencies.

    This is exposed publicly for re-use by the csvcubed-pmd project.

    :return: An `rdflib.ConjunctiveGraph`
    """

    _logger.debug("Loading RDF dependencies")

    rdf = rdflib.ConjunctiveGraph()

    dependencies_to_load = select_metadata_dependencies(csvw_metadata_rdf_graph)

    for dependency in dependencies_to_load:
        this_dependency_rdf = rdf.get_context(dependency.data_dump)
        if any(this_dependency_rdf):
            _logger.debug(
                "Skipping dependency '%s' as it has already been loaded.",
                dependency.data_dump,
            )
            continue

        _logger.debug(
            "Loading dataset dependency '%s' covering uriSpace '%s' in dataset '%s'",
            dependency.data_dump,
            dependency.uri_space,
            dependency.data_set,
        )

        expected_format = guess_format(dependency.data_dump) or "json-ld"
        _logger.debug("Anticipated RDF format: '%s'.", expected_format)

        this_dependency_rdf.load(dependency.data_dump, format=expected_format)

        # Process all of the dependencies which this file requires.
        dependencies_to_load += select_metadata_dependencies(this_dependency_rdf)

        rdf += this_dependency_rdf

    return rdf
