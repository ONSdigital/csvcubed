from io import BytesIO
import logging
from typing import Optional
from pathlib import Path

# from click import Path
import requests

_logger = logging.getLogger(__name__)


def create_local_copy_response(
    path_to_local_file: Path,
    request: requests.PreparedRequest,
    response: Optional[requests.Response] = None,
) -> requests.Response:
    """
    Generates the response object that contains the local copy file path of the requested file and then returns it.
    """
    _logger.warning(
        f"Unable to load json document from given URL. Attempting to load local storage copy of file {path_to_local_file} instead."
    )

    successful_response = requests.Response()

    successful_response.status_code = 200

    successful_response.raw = BytesIO(bytes(path_to_local_file.read_text(), "utf-8"))
    successful_response.url = path_to_local_file.as_uri()

    successful_response.encoding = "utf-8"

    if response is not None:
        successful_response.history = [response]

    successful_response.reason = "OK"
    successful_response.request = request

    return successful_response
