"""
JSON Utilities
--------------

Utilities for working with JSON
"""
import json
import logging
import os.path
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Union
from urllib.parse import urlparse

from jsonschema import RefResolver

from csvcubed.utils.uri import looks_like_uri

from .cache import session

_logger = logging.getLogger(__name__)


def load_json_document(file_uri_or_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Accepts a :obj:`file_uri` and returns the deserialised JSON document as a python dictionary.

        :obj:`file_uri` accepts URLs such as: `https://example.com/some-document.json`
        :obj:`file_uri` accepts file paths such as: `file:///User/MyUser/some-document.json`
        :obj:`file_uri` accepts :class:`pathlib.Path`, e.g.: `Path('/User/MyUser/some-document.json')`

    :return: :obj:`Dict[str, Any]`
    """
    if isinstance(file_uri_or_path, Path):
        return _load_json_from_path(file_uri_or_path)
    else:
        url = urlparse(file_uri_or_path)
        if url.scheme == "file":
            file_path = Path(
                os.path.normpath(file_uri_or_path)
                .removeprefix("file:\\")
                .removeprefix("file:")
            )
            return _load_json_from_path(file_path)
        else:
            # Treat it as a URL
            _logger.debug("Loading JSON from URL %s", file_uri_or_path)
            http_response = session.get(file_uri_or_path)
            if not http_response.ok:
                raise Exception(
                    f"Error loading JSON from URL '{file_uri_or_path}'. HTTP response: {http_response}."
                )
            try:
                return http_response.json()
            except Exception as e:
                raise Exception(
                    f"Error loading JSON from URL '{file_uri_or_path}'"
                ) from e


def _load_json_from_path(path: Path) -> Dict[str, Any]:
    _logger.debug("Loading JSON from file %s", path)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading JSON from file at '{path}'") from e


# Credit: Antti Haapala: https://stackoverflow.com/questions/8230315/how-to-json-serialize-sets
def serialize_sets(obj):
    """
    Converts any sets in the object to a list for json serialisation
    """
    if isinstance(obj, set):
        return list(obj)

    return obj


def to_json_path(path_parts: Iterable[Union[str, int]]) -> str:
    """
    Converts an iterable of path parts into a JSON path compatible with https://pypi.org/project/jsonpath-ng/
    https://goessner.net/articles/JsonPath/
    """
    string_path_parts = []
    for path_part in path_parts:
        if isinstance(path_part, str):
            if re.search(r"[.\[\]'\s]", path_part):
                # Path part contains a reserved character and needs escaping
                escaped_path_part = path_part.replace("'", r"\'")
                string_path_parts.append(f".'{escaped_path_part}'")
            else:
                string_path_parts.append(f".{path_part}")
        elif isinstance(path_part, int):
            string_path_parts.append(f"[{path_part}]")
        else:
            raise ValueError(
                f"Unhandled JSON path_part '{path_part}' of type {type(path_part)}."
            )

    return "$" + "".join(string_path_parts)


def resolve_path(
    path_to_resolve: List[Union[str, int]], within: dict
) -> Iterable[dict]:
    """
    Returns an iterable containing the JSON objects along the entire `path_to_resolve` ensuring to follow JSON schema
      `$ref` links.
    """
    if not any(path_to_resolve):
        return []

    resolver = RefResolver.from_schema(within)
    pointer = 1

    while pointer <= len(path_to_resolve):
        _, value = resolver.resolve(
            "#/" + "/".join([str(e) for e in path_to_resolve][:pointer])
        )
        yield value

        if "$ref" in value:
            next_ref = value["$ref"]
            if looks_like_uri(next_ref):
                value = resolver.resolve_from_url(next_ref)
            else:
                _, value = resolver.resolve(next_ref)

            yield value

            yield from resolve_path(path_to_resolve[pointer:], value)
            break

        pointer += 1
