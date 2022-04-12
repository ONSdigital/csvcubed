"""
CSV-W
-----

Utils for working with CSV-Ws.
"""
import json
import logging
from typing import Set, List, Optional, Union, Tuple
from pathlib import Path
import urllib.parse
import requests
from rdflib import Graph

from .json import load_json_document
from .uri import looks_like_uri


_logger = logging.getLogger(__name__)


def get_dependent_local_files(csvw_metadata_file: Path) -> Set[Path]:
    """
    N.B. this is a bit of a rough-and-ready function and may not catch *all* dependencies listed.
    However, it should work for the style of CSV-Ws that we currently generate.

    :return: a list of all of the local dependencies specified in a CSV-W file.
    """
    _logger.debug("Searching for local dependencies in CSV-W at %s", csvw_metadata_file)
    table_group = _load_table_group(csvw_metadata_file)

    base_path = _get_base_path(csvw_metadata_file.parent, table_group)
    if not isinstance(base_path, Path):
        _logger.debug(
            "CSV-W base path is a URI '%s'. There are no relatively defined local dependent files.",
            base_path,
        )
        return set()

    dependent_local_files: Set[Path] = _get_url_and_table_schema_path_for_table(
        base_path, table_group
    )

    tables: List[dict] = table_group.get("tables", [])
    for table in tables:
        dependent_local_files |= _get_url_and_table_schema_path_for_table(
            base_path, table
        )

    _logger.debug("Found dependent local files %s", dependent_local_files)
    return dependent_local_files


def get_first_table_schema(
    csvw_metadata_file: Path,
) -> Optional[Tuple[Optional[str], dict]]:
    """
    :return: the first table Schema found in the CSV-W metadata document, if there is one.
    """

    def _get_table_schema(
        base_path: Union[Path, str], table: dict
    ) -> Optional[Tuple[Optional[str], dict]]:
        table_schema = table.get("tableSchema")
        table_url = table.get("url")
        if table_schema is None:
            return None
        elif isinstance(table_schema, str):
            if looks_like_uri(table_schema):
                return table_url, json.loads(requests.get(table_schema).text)
            else:
                if isinstance(base_path, Path):
                    with open(base_path / table_schema, "r") as f:
                        return table_url, json.load(f)
                else:
                    schema_url = urllib.parse.urljoin(base_path + "/", table_schema)
                    return table_url, json.loads(requests.get(schema_url).text)
        elif isinstance(table_schema, dict):
            return table_url, table_schema
        else:
            raise ValueError(f"Unexpected type for tableSchema: {type(table_schema)}")

    table_group = _load_table_group(csvw_metadata_file)
    base_path = _get_base_path(csvw_metadata_file.parent, table_group)

    table_group_schema = _get_table_schema(base_path, table_group)
    if table_group_schema is not None:
        _logger.debug(
            "Found first table schema (%s) in CSV-W at %s",
            table_group_schema[0],
            csvw_metadata_file,
        )
        return table_group_schema

    tables = table_group.get("tables")
    if tables is not None and isinstance(tables, list) and len(tables) > 0:
        for table in tables:
            table_schema = _get_table_schema(base_path, table)
            if table_schema is not None:
                _logger.debug(
                    f"Found first table schema (%s) in CSV-W at %s",
                    table_schema[0],
                    csvw_metadata_file,
                )
                return table_schema

    _logger.warning("Could not find table schema in CSV-W at %s", csvw_metadata_file)
    return None


def _load_table_group(csvw_metadata_file: Path) -> dict:
    with open(csvw_metadata_file, "r") as f:
        table_group = json.load(f)
        assert isinstance(table_group, dict)
    return table_group


def _get_url_and_table_schema_path_for_table(base_path: Path, table: dict) -> Set[Path]:
    dependent_local_files = set()

    table_url = table.get("url")
    table_schema = table.get("tableSchema")

    if table_url is not None and str(table_url).strip() != "":
        table_url = str(table_url).strip()
        _logger.debug("Found CSV dependency (%s) in 'url' field.", table_url)
        if not looks_like_uri(table_url):
            dependent_local_files.add(base_path / table_url)
    if table_schema is not None and isinstance(table_schema, str):
        table_schema_path = table_schema.strip()
        _logger.debug(
            "Found table schema dependency (%s) in 'tableSchema' field.",
            table_schema_path,
        )
        if not looks_like_uri(table_schema_path):
            dependent_local_files.add(base_path / table_schema_path)

    return dependent_local_files


def _get_base_path(preliminary_base_path: Path, table_group: dict) -> Union[Path, str]:
    """
    :return: :obj:`pathlib.Path` (local file path) OR :obj:`str` (URI path)
    """
    context = table_group["@context"]
    if isinstance(context, list) and len(context) > 1:
        context_obj = context[1]
        assert isinstance(context_obj, dict)
        base = context_obj.get("@base")
        if base is not None and isinstance(base, str) and len(base.strip()) > 0:
            if looks_like_uri(base):
                # base path is a URI, so none of the files will be local.
                return base
            base_path = Path(base)
            if base_path.is_absolute():
                return base_path
            else:
                return preliminary_base_path / base
    return preliminary_base_path


def load_table_schema_file_to_graph(
    table_schema_file_path: Union[str, Path], graph: Graph
) -> None:
    """
    Given a tableSchema file definition at :obj:`table_schema_file_path`,
     load the metadata as CSV-W flavoured RDF into the graph :obj:`graph`.
    """
    table_schema_document = load_json_document(table_schema_file_path)

    # > When a schema is referenced by URL, this URL becomes the value of the @id property in the
    # > normalized schema description, and thus the value of the schema annotation on the table.
    #
    # https://www.w3.org/TR/2015/REC-tabular-metadata-20151217/#table-schema
    table_schema_document["@id"] = str(table_schema_file_path)

    # Provide the context to help generate all of the necessary RDF.
    table_schema_document["@context"] = "http://www.w3.org/ns/csvw"

    table_schema_document_json = json.dumps(table_schema_document)

    graph.parse(
        data=table_schema_document_json,
        publicID=str(table_schema_file_path),
        format="json-ld",
    )
