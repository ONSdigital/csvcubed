"""
Pull CSV-W
----------

Functionality to pull a CSV-W and all of its relative dependencies to the local filesystem.
"""
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Union
from urllib.parse import urljoin, urlparse

import rdflib
from requests.exceptions import HTTPError

from csvcubed.utils.cache import session
from csvcubed.utils.json import load_json_document
from csvcubed.utils.rdf import parse_graph_retain_relative
from csvcubed.utils.tableschema import add_triples_for_file_dependencies
from csvcubed.utils.uri import looks_like_uri

_logger = logging.getLogger(__name__)


def pull(csvw_metadata_url: str, output_dir: Path) -> None:
    """
    Pull all the relative dependencies of a CSV-W metadata file down to the :obj:`output_dir`.
    """
    _logger.info(
        "Pulling CSV-W '%s' into output directory '%s'.", csvw_metadata_url, output_dir
    )

    output_dir.mkdir(exist_ok=True, parents=True)

    if looks_like_uri(csvw_metadata_url):
        csvw_metadata_file_name = _get_file_name_from_url(csvw_metadata_url)
        _download_to_file(csvw_metadata_url, output_dir / csvw_metadata_file_name)
        base_path_for_relative_files = urlparse(urljoin(csvw_metadata_url, ".")).path
    else:
        _copy_local_dependency(csvw_metadata_url, output_dir)
        base_path_for_relative_files = Path(csvw_metadata_url).absolute().parent

    _logger.debug("Base path for relative files '%s'", base_path_for_relative_files)

    for absolute_dependency_path in _get_csvw_dependencies(csvw_metadata_url):
        relative_dependency_path = os.path.relpath(
            urlparse(absolute_dependency_path).path, start=base_path_for_relative_files
        )
        _logger.debug("Relative dependency path '%s'", relative_dependency_path)

        output_file = output_dir / relative_dependency_path
        output_file.parent.mkdir(exist_ok=True, parents=True)
        if looks_like_uri(csvw_metadata_url):
            _download_to_file(absolute_dependency_path, output_file)
        else:
            _copy_local_dependency(absolute_dependency_path, output_file)


def _copy_local_dependency(csvw_metadata_path: str, output_location: Path) -> None:
    _logger.debug("Treating location '%s' as a local Path", csvw_metadata_path)
    csvw_metadata_file_path = str(Path(csvw_metadata_path).absolute())
    _logger.info(
        "Copying file '%s' to %s.",
        csvw_metadata_file_path,
        output_location,
    )
    shutil.copy(csvw_metadata_file_path, output_location)
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


def _get_csvw_dependencies(metadata_file_url: str) -> Set[str]:
    """
    :return: A set containing all the URLs referenced by the CSV-W converted to absolute form.
    """

    _logger.debug("Locating dependencies for '%s'", metadata_file_url)
    table_group = _get_table_group_for_metadata_file(metadata_file_url)

    base_url = _get_context_base_url(table_group.get("@context"))
    if base_url is None:
        base_url = metadata_file_url
    elif not looks_like_uri(base_url):
        base_url = urljoin(metadata_file_url, base_url)
    _logger.debug("Absolute base URL for document: '%s'", base_url)

    dependencies = set(_get_csv_w_spec_dependencies(table_group))
    dependencies |= _get_rdf_file_dependencies(metadata_file_url)

    absolute_dependencies = {
        path if looks_like_uri(path) else urljoin(base_url, path)
        for path in dependencies
    }

    _logger.debug("Found CSV-W spec dependencies %s", absolute_dependencies)

    return absolute_dependencies


def _get_csv_w_spec_dependencies(table_group: dict) -> Iterable[str]:
    _logger.debug("Locating CSV-W spec file dependencies.")
    # Embedded tables
    tables = table_group.get("tables", [])

    # If none, assume csvw represents a single table
    if not any(tables):
        _logger.debug("No tables found, assuming top-level object is single table.")
        tables = [table_group]

    for table in tables:
        table_url = table.get("url")
        schema = table.get("tableSchema")

        if table_url is not None and str(table_url).strip() != "":
            _logger.debug("Found table located at url '%s'", table_url)
            yield str(table_url).strip()
        if schema is not None and isinstance(schema, str) and schema.strip() != "":
            _logger.debug("Found schema defined in file '%s'", schema)
            yield schema.strip()


def _get_rdf_file_dependencies(metadata_file_url: str) -> Set[str]:
    """
    Extract file dependencies defined in RDF.

    If you want to load the triples, you should not use this function as this loads all dependent triples and
    then throws most of them away.

    :return: A list of paths specifying the location of file dependencies.
    """

    table_group_graph = rdflib.ConjunctiveGraph()

    parse_graph_retain_relative(
        metadata_file_url,
        format="json-ld",
        graph=table_group_graph.get_context(metadata_file_url),
    )

    # This certainly isn't the most efficient approach at dependency resolution, but it's convenient right now.
    add_triples_for_file_dependencies(
        table_group_graph,
        paths_relative_to=metadata_file_url,
        follow_relative_path_dependencies_only=True,
    )

    rdf_file_dependencies = {
        str(c.identifier)
        for c in table_group_graph.contexts()
        if isinstance(c.identifier, rdflib.URIRef)
        and c.identifier != rdflib.URIRef(metadata_file_url)
    }

    _logger.debug("Found RDF File dependencies %s", rdf_file_dependencies)

    return rdf_file_dependencies


def _get_table_group_for_metadata_file(metadata_file: str) -> Dict:
    _logger.debug("Acquiring table group for metadata file '%s'", metadata_file)
    if looks_like_uri(metadata_file):
        _logger.debug("Downloading metadata file '%s'", metadata_file)

        with session.cache_disabled():
            _logger.debug("Temporarily disabling HTTP(s) cache to ensure latest data.")
            return load_json_document(metadata_file)
    else:
        _logger.debug("Opening metadata file '%s'", metadata_file)
        with open(Path(metadata_file), "r") as f:
            return json.load(f)


def _get_file_name_from_url(url: str) -> str:
    file_name = os.path.basename(urlparse(url).path)
    _logger.debug("Extracted file name '%s' from URL '%s'.", file_name, url)
    return file_name


def _download_to_file(rel_dep_url: str, output_file: Path) -> None:
    _logger.info("Downloading '%s' to '%s'.", rel_dep_url, output_file)

    with open(output_file, "wb+") as f:
        with session.cache_disabled():
            _logger.debug("Temporarily disabling HTTP(s) cache to ensure latest data.")
            response = session.get(rel_dep_url)
            if not response.ok:
                raise HTTPError(
                    f"Failed to get url {rel_dep_url} with status code {response.status_code}. "
                    f"With text response: {response.text}"
                )
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

    _logger.debug("Download of '%s' complete.", rel_dep_url)
