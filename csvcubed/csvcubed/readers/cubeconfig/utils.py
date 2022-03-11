import logging
from pathlib import Path
from csvcubed.utils.json import load_json_from_uri, read_json_from_file


def load_resource(resource_path: Path) -> dict:
    """
    Load a json schema document from either a File or URI
    """
    schema: dict = {}

    if resource_path.parts[0].startswith('http'):
        schema = load_json_from_uri(str(resource_path))

    else:
        if not resource_path.is_absolute():
            resource_path = resource_path.resolve()
        schema = read_json_from_file(resource_path)

    return schema


_logger = logging.getLogger(__name__)


