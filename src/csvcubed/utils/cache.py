import copy
from io import BytesIO, StringIO
import logging
from pathlib import Path
from typing import Dict
import requests
from requests_cache import CachedSession

from csvcubed.definitions import APP_ROOT_DIR_PATH

_logger = logging.getLogger(__name__)


# def _hook_for_http_failure(response: requests.Response, *args, **kwargs):
#     print(f"The status code is: {response.status_code}")
#     get_local_version_instead = get_url_to_file_path_map()
#     if response.status_code >= 200 and response.status_code <= 399:
#         print("This was successful")
#     else:
#         print("Not successful")
#         # print(f"could not retrieve the document at: {response.url}")
#         trimmed_url = str(response.url).removeprefix("https:")
#         path_to_local_file = get_local_version_instead[
#             trimmed_url[: len(trimmed_url) - 1]
#         ]
#         print(f"The local file path is: {path_to_local_file}")
#         try:
#             #1 We could warn the user here about the request failure and inform about attempting to use the local file, or see #2
#             _logger.warning(f"Unable to load json document from given URL. Attempting to load local storage copy of file {path_to_local_file} instead.")

#             # The below is a response object that can be used to manually return the local copy of the file successfully.

#             successful_response = requests.Response()

#             successful_response.status_code = 200

#             successful_response.raw = BytesIO(bytes(path_to_local_file.read_text(), "utf-8"))

#             successful_response.url = path_to_local_file.as_uri()

#             successful_response.encoding = "utf-8"

#             successful_response.history = [response]
#             successful_response.reason = "OK"
#             successful_response.request = response.request


#             return successful_response

#             #2 Or perhaps we could log the warning here only if/after the local copy has been succcessfully retrieved?
#             #logger.warning("Unable to load json document from given URL. File has been loaded from local storage instead.")

#         except Exception as e: #What type of error are we expecting? Maybe FileNotFound?
#             raise Exception(f"Error loading JSON from file at '{path_to_local_file}'") from e

#         # response.url = path_to_local_file
#         return response

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


def get_url_to_file_path_map() -> Dict[str, Path]:
    """
    todo: add comment here
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


_map_url_to_file_path = get_url_to_file_path_map()

from requests.adapters import BaseAdapter, HTTPAdapter
from urllib3.exceptions import NewConnectionError
from requests.exceptions import JSONDecodeError


class CustomAdapterServeSomeFilesLocally(BaseAdapter):
    http_adapter: HTTPAdapter

    def __init__(self):
        self.http_adapter = HTTPAdapter()

    def send(
        self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None
    ):
        print(f"This is the HTTP(s) adapter sending the request: {request.url}")
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
            # except requests.exceptions.RequestException as e:
            try:
                print("The connection error has been found")

                trimmed_url = str(request.url).removeprefix("https:")
                path_to_local_file = _map_url_to_file_path[
                    trimmed_url[: len(trimmed_url) - 1]
                ]
                print(f"The local file path is: {path_to_local_file}")

                _logger.warning(
                    f"Unable to load json document from given URL. Attempting to load local storage copy of file {path_to_local_file} instead."
                )

                # The below is a response object that can be used to manually return the local copy of the file successfully.

                successful_response = requests.Response()

                successful_response.status_code = 200

                successful_response.raw = BytesIO(
                    bytes(path_to_local_file.read_text(), "utf-8")
                )

                successful_response.url = path_to_local_file.as_uri()

                successful_response.encoding = "utf-8"

                # successful_response.history = [response]
                successful_response.reason = "OK"
                successful_response.request = request

                return successful_response

            except FileNotFoundError as e:
                raise Exception(
                    f"Error loading JSON from file at '{path_to_local_file}'"
                ) from e

        # if response.status_code in (4**, 5**)
        # then try recovering to a local copy of the file
        return response

    def close(self) -> None:
        self.http_adapter.close()


session = CachedSession(cache_control=True, use_cache_dir=True)
session.mount("http://", CustomAdapterServeSomeFilesLocally())
session.mount("https://", CustomAdapterServeSomeFilesLocally())

# session.hooks["response"] = [_hook_for_http_failure]
