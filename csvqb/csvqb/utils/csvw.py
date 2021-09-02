"""
CSV-W
-----

Utils for working with CSV-Ws.
"""
import json
from typing import Set, List, Optional
from pathlib import Path

from .uri import looks_like_uri


def get_dependent_local_files(csvw_metadata_file: Path) -> Set[Path]:
    """
    N.B. this is a bit of a rough-and-ready function and may not catch *all* dependencies listed.
    However, it should work for the style of CSV-Ws that we currently generate.

    :return: a list of all of the local dependencies specified in a CSV-W file.
    """

    with open(csvw_metadata_file, "r") as f:
        table_group = json.load(f)
        assert isinstance(table_group, dict)

    dependent_local_files: Set[Path] = set()

    base_path = _get_base_path(csvw_metadata_file.parent, table_group)
    if base_path is None:
        return set()

    dependent_local_files |= _get_url_and_table_schema_path_for_table(
        base_path, table_group
    )

    tables: List[dict] = table_group.get("tables", [])
    for table in tables:
        dependent_local_files |= _get_url_and_table_schema_path_for_table(
            base_path, table
        )

    return dependent_local_files


def _get_url_and_table_schema_path_for_table(base_path: Path, table: dict) -> Set[Path]:
    dependent_local_files = set()

    table_url = table.get("url")
    table_schema = table.get("tableSchema")

    if table_url is not None and str(table_url).strip() != "":
        table_url = str(table_url).strip()
        if not looks_like_uri(table_url):
            dependent_local_files.add(base_path / table_url)
    if table_schema is not None and isinstance(table_schema, str):
        table_schema_path = table_schema.strip()
        if not looks_like_uri(table_schema_path):
            dependent_local_files.add(base_path / table_schema_path)

    return dependent_local_files


def _get_base_path(preliminary_base_path: Path, table_group: dict) -> Optional[Path]:
    context = table_group["@context"]
    if isinstance(context, list) and len(context) > 1:
        context_obj = context[1]
        assert isinstance(context_obj, dict)
        base = context_obj.get("@base")
        if base is not None and isinstance(base, str) and len(base.strip()) > 0:
            if looks_like_uri(base):
                # base path is a URI, so none of the files will be local.
                return None
            base_path = Path(base)
            if base_path.is_absolute():
                return base_path
            else:
                return preliminary_base_path / base
    else:
        return preliminary_base_path
