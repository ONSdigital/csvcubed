import copy
from io import BytesIO, StringIO
import logging
from pathlib import Path
from typing import Dict, Optional, Union
import requests
from requests.adapters import BaseAdapter, HTTPAdapter
from requests_cache import CachedSession


from csvcubed.definitions import APP_ROOT_DIR_PATH

_logger = logging.getLogger(__name__)

_hard_codes_map_url_to_file_path = {
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
    Creates a dictionary that maps URLs requested by load_json_document to their corresponding local storage files,
    so they can be retrieved in case the HTTP request fails during csvcubed build process.
    """

    templates_dir = APP_ROOT_DIR_PATH / "readers" / "cubeconfig" / "v1_0" / "templates"

    template_files = templates_dir.rglob("**/*.json*")

    if not any(template_files):
        raise ValueError(f"Couldn't find template files in {templates_dir}.")

    map_uri_to_file_path = copy.deepcopy(_hard_codes_map_url_to_file_path)

    for template_file in template_files:
        relative_file_path = str(template_file.relative_to(templates_dir))
        uri = (
            "//raw.githubusercontent.com/GSS-Cogs/csvcubed/main/src/csvcubed/readers/cubeconfig/v1_0/templates/"
            + relative_file_path
        )
        map_uri_to_file_path[uri] = template_file

    return map_uri_to_file_path


map_url_to_file_path = _get_url_to_file_path_map()


class CustomAdapterServeSomeFilesLocally(BaseAdapter):
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
            try:
                _logger.debug("The connection error has been found")

                path_to_local_file = generate_path_to_local_file(request.url)

                _logger.debug("The local file path is: %s", path_to_local_file)

                return create_local_copy_response(path_to_local_file, request)

            except Exception:
                raise FileNotFoundError(
                    f"URL {request.url} did not produce a response and a local copy could not be found at the corresponding mapped path."
                ) from e

        if response.status_code >= 400 and response.status_code < 600:
            _logger.info(f"The status code is {response.status_code}")
            try:
                path_to_local_file = generate_path_to_local_file(request.url)
                return create_local_copy_response(path_to_local_file, request, response)

            except Exception:
                raise FileNotFoundError(
                    f"URL {request.url} produced a invalid response and a local copy could not be found at the corresponding mapped path."
                )

            # return create_local_copy_response(path_to_local_file, request, response)

        return response

    def close(self) -> None:
        self.http_adapter.close()


def generate_path_to_local_file(request_url: Union[str, None]) -> Path:
    if request_url is None:
        raise Exception

    trimmed_url = str(request_url).removeprefix("https:")
    if request_url[len(request_url) - 1] == "/":
        path_to_local_file = map_url_to_file_path.get(
            trimmed_url[: len(trimmed_url) - 1]
        )
    else:
        path_to_local_file = map_url_to_file_path.get(trimmed_url)

    if path_to_local_file is None:
        raise Exception

    return path_to_local_file


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

    if path_to_local_file is not None:
        successful_response.raw = BytesIO(
            bytes(path_to_local_file.read_text(), "utf-8")
        )
    successful_response.url = path_to_local_file.as_uri()

    successful_response.encoding = "utf-8"

    if response is not None:
        successful_response.history = [response]

    successful_response.reason = "OK"
    successful_response.request = request

    return successful_response


session = CachedSession(cache_control=True, use_cache_dir=True)
session.mount("http://", CustomAdapterServeSomeFilesLocally())
session.mount("https://", CustomAdapterServeSomeFilesLocally())
