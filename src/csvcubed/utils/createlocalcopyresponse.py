import copy
import logging
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional

import requests
from requests.adapters import BaseAdapter, HTTPAdapter

from csvcubed.definitions import APP_ROOT_DIR_PATH
from csvcubed.utils.log import debug_log_exception

_logger = logging.getLogger(__name__)

_hard_coded_map_url_to_file_path = {
    "//purl.org/csv-cubed/qube-config/v1.0": APP_ROOT_DIR_PATH
    / "schema"
    / "cube-config"
    / "v1_0"
    / "schema.json",
    "//purl.org/csv-cubed/qube-config/v1.1": APP_ROOT_DIR_PATH
    / "schema"
    / "cube-config"
    / "v1_1"
    / "schema.json",
    "//purl.org/csv-cubed/qube-config/v1.2": APP_ROOT_DIR_PATH
    / "schema"
    / "cube-config"
    / "v1_2"
    / "schema.json",
    "//purl.org/csv-cubed/qube-config/v1.3": APP_ROOT_DIR_PATH
    / "schema"
    / "cube-config"
    / "v1_3"
    / "schema.json",
    "//purl.org/csv-cubed/qube-config/v1.4": APP_ROOT_DIR_PATH
    / "schema"
    / "cube-config"
    / "v1_4"
    / "schema.json",
    "//purl.org/csv-cubed/qube-config/v1": APP_ROOT_DIR_PATH
    / "schema"
    / "cube-config"
    / "v1_4"
    / "schema.json",  # v1 defaults to latest minor version of v1.*.
    "//purl.org/csv-cubed/codelist-config/v1.0": APP_ROOT_DIR_PATH
    / "schema"
    / "codelist-config"
    / "v1_0"
    / "schema.json",
    "//purl.org/csv-cubed/codelist-config/v1.1": APP_ROOT_DIR_PATH
    / "schema"
    / "codelist-config"
    / "v1_1"
    / "schema.json",
    "//purl.org/csv-cubed/code-list-config/v1": APP_ROOT_DIR_PATH
    / "schema"
    / "codelist-config"
    / "v1_1"
    / "schema.json",  # v1 defaults to latest minor version of v1.*.
}


def _get_url_to_file_path_map() -> Dict[str, Path]:
    """
    Dynamically adds template URLs + corresponding files to the hardcoded map:
    _hard_coded_map_url_to_file_path for use in schema mocking and when a local
    copy of a file must be retrieved when an HTTP(S) request fails. Both github
    and purl URLs are mapped for offline scenarios.
    """

    templates_dir = APP_ROOT_DIR_PATH / "readers" / "cubeconfig" / "v1_0" / "templates"

    template_files = templates_dir.rglob("**/*.json*")

    if not any(template_files):
        raise ValueError(f"Couldn't find template files in {templates_dir}.")

    map_uri_to_file_path = copy.deepcopy(_hard_coded_map_url_to_file_path)

    for template_file in template_files:
        relative_file_path = str(template_file.relative_to(templates_dir))
        github_uri = (
            "//raw.githubusercontent.com/GSS-Cogs/csvcubed/main/src/csvcubed/readers/cubeconfig/v1_0/templates/"
            + relative_file_path
        )
        map_uri_to_file_path[github_uri] = template_file

        purl_uri = "//purl.org/csv-cubed/qube-config/templates/" + relative_file_path
        map_uri_to_file_path[purl_uri] = template_file

    return map_uri_to_file_path


map_url_to_file_path = _get_url_to_file_path_map()


def _generate_path_to_local_file(request_url: Optional[str]) -> Optional[Path]:
    _logger.debug(
        "Attempting to find local file to served up for failed HTTP request '%s'",
        request_url,
    )

    if request_url is None:
        _logger.debug("Request URL is None, no matching local file.")
        return None

    trimmed_url = (
        str(request_url).removeprefix("https:").removeprefix("http:").removesuffix("/")
    )
    path_to_local_file = map_url_to_file_path.get(trimmed_url)

    _logger.debug("Proposed matching local file: '%s'", path_to_local_file)

    return path_to_local_file


class AdapterToServeLocalFileWhenHTTPRequestFails(BaseAdapter):
    """
    A custom transport adapter which returns a local copy of the requested file only
    in the event that an HTTP(S) request fails likely due to connectivity issues.
    """

    http_adapter: HTTPAdapter

    def __init__(self):
        self.http_adapter = HTTPAdapter()

    def send(
        self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None
    ):
        _logger.debug(
            "This is the HTTP(s) adapter sending the request: %s", request.url
        )
        try:
            response = self.http_adapter.send(
                request,
                stream=stream,
                timeout=timeout,
                verify=verify,
                cert=cert,
                proxies=proxies,
            )

        except requests.exceptions.ConnectionError as e:
            debug_log_exception(_logger, e)
            _logger.error("A connection error has been found")

            path_to_local_file = _generate_path_to_local_file(request.url)
            if path_to_local_file is None:
                raise FileNotFoundError(
                    f"URL '{request.url}' did not produce a response and a local copy could not be found."
                ) from e

            _logger.error("The local file path is: %s", path_to_local_file)

            return _create_local_copy_response(path_to_local_file, request)

        if response.status_code >= 400 and response.status_code < 600:
            _logger.info(f"The status code is {response.status_code}")
            path_to_local_file = _generate_path_to_local_file(request.url)
            if path_to_local_file is None:
                raise FileNotFoundError(
                    f"URL '{request.url}' produced a invalid response and a local copy could not be found."
                )

            return _create_local_copy_response(path_to_local_file, request, response)

        return response

    def close(self) -> None:
        self.http_adapter.close()


def _create_local_copy_response(
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
