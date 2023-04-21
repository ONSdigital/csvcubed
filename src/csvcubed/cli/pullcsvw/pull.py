"""
Pull CSV-W
----------

Functionality to pull a CSV-W and all of its relative dependencies to the local filesystem.
"""
import json
import logging
import os
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Generic, List, Optional, Set, TypeVar, Union
from urllib.parse import urljoin, urlparse

import rdflib
from requests.exceptions import HTTPError

from csvcubed.utils.cache import session
from csvcubed.utils.json import load_json_document
from csvcubed.utils.rdf import parse_graph_retain_relative
from csvcubed.utils.tableschema import add_triples_for_file_dependencies
from csvcubed.utils.uri import file_uri_to_path, looks_like_uri

_logger = logging.getLogger(__name__)

TPath = TypeVar("TPath", bound=Union[str, Path])
"""
Either a string (URL) for a remotely stored CSV-W or a Path for a locally stored CSV-W.
"""


def pull(csvw_metadata_url: str, output_dir: Path) -> None:
    """
    Pull all the relative dependencies of a CSV-W metadata file down to the :obj:`output_dir`.
    """
    _logger.info(
        "Pulling CSV-W '%s' into output directory '%s'.", csvw_metadata_url, output_dir
    )

    output_dir.mkdir(exist_ok=True, parents=True)

    csvw_puller = (
        HttpCsvWPuller(csvw_metadata_url)
        if looks_like_uri(csvw_metadata_url)
        else FileCsvWPuller(Path(csvw_metadata_url))
    )

    csvw_puller.pull(output_dir)


@dataclass
class CsvWPuller(Generic[TPath], ABC):
    csvw_metadata_path: TPath

    def pull(self, output_dir: Path) -> None:
        """
        Pulls the CSV-W into the output directory.
        """
        self._pull_resource_to_dir(self.csvw_metadata_path, output_dir)
        for (
            absolute_dependency_path
        ) in self._get_csvw_dependencies_follow_relative_only():
            self._pull_resource_to_dir(absolute_dependency_path, output_dir)

    @abstractmethod
    def _pull_resource_to_dir(self, absolute_path: TPath, output_dir: Path) -> None:
        ...

    @abstractmethod
    def _get_table_group(self) -> Dict:
        """
        Returns the table group for the CSV-W metadata file.
        """
        ...

    @abstractmethod
    def _get_default_csv_w_base_path(self) -> TPath:
        """
        Returns the default base path for the document, assuming that a `@base` URL hasn't been set in the context.

        i.e. Where all the URLs are relative to (by default).
        """
        ...

    @abstractmethod
    def _join_relative_path(self, base_path: TPath, relative_path: str) -> TPath:
        """
        Join a relative path onto some base path.
        """
        ...

    @abstractmethod
    def _get_unique_identifier(self) -> str:
        """
        Return a unique string identifying this metadata file.
        """
        ...

    @abstractmethod
    def _map_rdflib_uri_to_path(self, rdflib_uri: str) -> TPath:
        """
        Map an rdflib URI representing a path to a TPath.
        """
        ...

    def _get_csvw_dependencies_follow_relative_only(
        self,
    ) -> Set[TPath]:
        """
        :return: A set containing all the relative URLs referenced by the CSV-W converted to absolute form.
        """

        _logger.debug("Locating dependencies for '%s'", self.csvw_metadata_path)
        dependencies = self._get_csv_w_spec_dependencies_follow_relative_only()
        dependencies |= self._get_rdf_file_dependencies_follow_relative_only()

        _logger.debug("Found CSV-W spec dependencies %s", dependencies)

        return dependencies

    def _get_csvw_metadata_base_path(self, table_group: dict) -> TPath:
        base_url = _get_context_base_url(table_group.get("@context"))

        default_base_path = self._get_default_csv_w_base_path()

        if base_url is None:
            _logger.debug(
                "Absolute base path/URL for document: '%s'", default_base_path
            )
            return default_base_path
        elif looks_like_uri(base_url):
            # If you specify an absolute base_url then none of the dependencies are relative, so there's nothing to
            # download.
            raise AbsoluteBasePathError(base_url)

        base_path = self._join_relative_path(default_base_path, base_url)
        _logger.debug("Absolute base path/URL for document: '%s'", base_path)
        return base_path

    def _get_csv_w_spec_dependencies_follow_relative_only(self) -> Set[TPath]:
        table_group = self._get_table_group()
        dependencies = _get_csv_w_spec_dependencies(table_group)
        # N.B. Dependencies which are absolute because of an absolute base_url will never come into this function.
        absolute_dependencies = {d for d in dependencies if looks_like_uri(d)}
        for d in absolute_dependencies:
            _logger.warning(
                "Not downloading dependency '%s' since it is an absolute dependency.", d
            )

        try:
            base_path = self._get_csvw_metadata_base_path(table_group)
        except AbsoluteBasePathError as e:
            _logger.warning(
                "Metadata JSON document %s has absolute base URL %s. No relative dependencies to download.",
                self.csvw_metadata_path,
                e.base_url,
            )
            return set()

        return {
            self._join_relative_path(base_path, d)
            for d in dependencies
            if d not in absolute_dependencies
        }

    def _get_rdf_file_dependencies_follow_relative_only(self) -> Set[TPath]:
        """
        Extract file dependencies defined in RDF.

        If you want to load the triples, you should not use this function as this loads all dependent triples and
        then throws most of them away.

        :return: A list of paths specifying the location of file dependencies.
        """

        table_group_graph = rdflib.ConjunctiveGraph()

        metadata_file_identifier: str = self._get_unique_identifier()
        parse_graph_retain_relative(
            self.csvw_metadata_path,
            format="json-ld",
            graph=table_group_graph.get_context(metadata_file_identifier),
        )

        # This certainly isn't the most efficient approach at dependency resolution, but it's convenient right now.
        add_triples_for_file_dependencies(
            table_group_graph,
            paths_relative_to=self.csvw_metadata_path,
            follow_relative_path_dependencies_only=True,
        )

        rdf_file_dependencies = {
            self._map_rdflib_uri_to_path(str(c.identifier))
            for c in table_group_graph.contexts()
            if isinstance(c.identifier, rdflib.URIRef)
            and c.identifier != rdflib.URIRef(metadata_file_identifier)
        }

        _logger.debug("Found RDF File dependencies %s", rdf_file_dependencies)

        return rdf_file_dependencies


@dataclass
class FileCsvWPuller(CsvWPuller[Path]):
    """
    Pulls a CSV-W and its relative dependencies from one file-system location to another.
    """

    def __post_init__(self):
        self.csvw_metadata_path = self.csvw_metadata_path.absolute()

    def _pull_resource_to_dir(
        self, absolute_resource_path: Path, output_dir: Path
    ) -> None:
        # Need to decide where we should write the file to within the output directory.
        relative_dependency_path = absolute_resource_path.relative_to(
            self.csvw_metadata_path.parent
        )

        output_file = output_dir / relative_dependency_path
        output_file.parent.mkdir(exist_ok=True, parents=True)
        _copy_local_dependency(absolute_resource_path, output_file)

    def _get_table_group(self) -> Dict:
        _logger.debug("Opening metadata file '%s'", self.csvw_metadata_path)
        with open(self.csvw_metadata_path, "r") as f:
            return json.load(f)

    def _get_default_csv_w_base_path(self) -> Path:
        # Needs to be the parent directory so that when the paths get joined we don't end up with
        # paths like `.../thingy.csv-metadata.json/thingy.csv`
        return self.csvw_metadata_path.parent

    def _join_relative_path(self, base_path: Path, relative_path: str) -> Path:
        # `base_path` always represents the parent directory inside a FileCsvWPuller.
        # we need to include a trailing slash so that we end up with
        return file_uri_to_path(urljoin(base_path.as_uri() + "/", relative_path))

    def _get_unique_identifier(self) -> str:
        # The URI of the file path is good enough to uniquely identify the CSV-W metadata file.
        return self.csvw_metadata_path.as_uri()

    def _map_rdflib_uri_to_path(self, rdflib_uri: str) -> Path:
        return file_uri_to_path(rdflib_uri)


@dataclass
class HttpCsvWPuller(CsvWPuller[str]):
    """
    Pulls a CSV-W and its relative dependencies from an HTTP(s) location to the local file-system.
    """

    def _pull_resource_to_dir(
        self, absolute_resource_path: str, output_dir: Path
    ) -> None:
        # Need to decide where we should write the file to within the output directory.
        base_path_for_relative_files = urlparse(
            urljoin(self.csvw_metadata_path, ".")
        ).path

        output_path = output_dir / os.path.relpath(
            urlparse(absolute_resource_path).path,
            start=base_path_for_relative_files,
        )

        _logger.debug("Downloading %s to %s", absolute_resource_path, output_path)

        output_path.parent.mkdir(exist_ok=True, parents=True)

        _download_to_file(absolute_resource_path, output_path)

    def _get_table_group(self) -> Dict:
        _logger.debug("Downloading metadata file '%s'", self.csvw_metadata_path)

        with session.cache_disabled():
            _logger.debug("Temporarily disabling HTTP(s) cache to ensure latest data.")
            return load_json_document(self.csvw_metadata_path)

    def _get_default_csv_w_base_path(self) -> str:
        return self.csvw_metadata_path

    def _join_relative_path(self, base_path: str, relative_path: str) -> str:
        return urljoin(base_path, relative_path)

    def _get_unique_identifier(self) -> str:
        return self.csvw_metadata_path

    def _map_rdflib_uri_to_path(self, rdflib_uri: str) -> str:
        # A URI is already the native way to represent paths in this class.
        return rdflib_uri


@dataclass
class AbsoluteBasePathError(ValueError):
    """
    An exception to communicate that the base path of the CSV-W metadata document is an absolute URL.

    This means that there are no relative dependencies that we can download. This exception should be caught and a
    warning communicated to the user.
    """

    base_url: str


def _copy_local_dependency(path_to_copy: Path, output_location: Path) -> None:
    _logger.debug("Treating location '%s' as a local Path", path_to_copy)
    absolute_path_to_copy = path_to_copy.absolute()
    _logger.info(
        "Copying file '%s' to %s.",
        absolute_path_to_copy,
        output_location,
    )
    shutil.copy(absolute_path_to_copy, output_location)
    _logger.debug("File copy operation complete.")


def _get_context_base_url(context: Union[Dict, List, None]) -> Optional[str]:
    """N.B. This only works on the CSV-W subset of JSON-LD."""
    if context is None:
        _logger.debug("No CSV-W context so no explicit document base URL")
        return None
    elif not (isinstance(context, list) and len(context) == 2):
        _logger.debug("Context does not contain explicit document base URL")
        return None

    context_obj = context[1]

    if not isinstance(context_obj, dict):
        _logger.debug(
            "Context appears to be invalid and does not contain explicit document base URL"
        )
        return None

    base_url = context_obj.get("@base")
    _logger.debug("Context sets '%s' as explicit base_url", base_url)

    return base_url


def _get_csv_w_spec_dependencies(table_group: dict) -> Set[str]:
    """ """
    _logger.debug("Locating CSV-W spec file dependencies.")
    dependencies: Set[str] = set()

    # Embedded tables
    tables = table_group.get("tables", [])

    # If none, assume csvw represents a single table
    if not any(tables):
        _logger.debug("No tables found, assuming top-level object is single table.")
        tables = [table_group]

    for table in tables:
        table_url = table.get("url")
        schema = table.get("tableSchema")

        if table_url is not None:
            _logger.debug("Found table located at url '%s'", table_url)
            dependencies.add(str(table_url).strip())
        if schema is not None and isinstance(schema, str):
            _logger.debug("Found schema defined in file '%s'", schema)
            dependencies.add(schema.strip())

    return dependencies


def _get_file_name_from_url(url: str) -> str:
    file_name = os.path.basename(urlparse(url).path)
    _logger.debug("Extracted file name '%s' from URL '%s'.", file_name, url)
    return file_name


def _download_to_file(url_to_download: str, output_file: Path) -> None:
    _logger.info("Downloading '%s' to '%s'.", url_to_download, output_file)

    with open(output_file, "wb+") as f:
        with session.cache_disabled():
            _logger.debug("Temporarily disabling HTTP(s) cache to ensure latest data.")
            response = session.get(url_to_download)
            if not response.ok:
                raise HTTPError(
                    f"Failed to get url {url_to_download} with status code {response.status_code}. "
                    f"With text response: {response.text}"
                )
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

    _logger.debug("Download of '%s' complete.", url_to_download)
