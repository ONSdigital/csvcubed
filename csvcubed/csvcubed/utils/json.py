"""
JSON Utilities
--------------

Utilities for working with JSON
"""
import json
from typing import Dict, Any, Union
from pathlib import Path
import logging
from urllib.parse import urlparse

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
            file_path = Path(file_uri_or_path.removeprefix("file://"))
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