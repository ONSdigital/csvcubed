from pathlib import Path
from typing import Union

from csvcubed.utils.json import load_json_document
from csvcubed.utils.uri import looks_like_uri


def load_resource(resource_path: Union[str, Path]) -> dict:
    """
    Load a json schema document from either a File or URI
    """
    if isinstance(resource_path, str):
        if looks_like_uri(resource_path):
            return load_json_document(str(resource_path))
        else:
            resource_path = Path(resource_path)

    if not resource_path.is_absolute():
        resource_path = resource_path.resolve()
    return load_json_document(resource_path)
