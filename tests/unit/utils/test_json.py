import pytest
import requests_mock
import json

from tests.unit.test_baseunit import get_test_cases_dir
from csvcubed.utils.json import load_json_document
from csvcubed.utils.cache import map_url_to_file_path, session
from csvcubed.definitions import APP_ROOT_DIR_PATH

_json_test_cases_dir = get_test_cases_dir() / "utils" / "json"


def test_loading_json_from_file_uri():
    """
    Ensure we can load a JSON document from the local file system with a `file://` URI.
    """

    document = load_json_document(
        "file://" + str(_json_test_cases_dir / "json-document.json")
    )
    assert document.get("This") == "Is Valid JSON"


def test_loading_json_from_file_path():
    """
    Ensure we can load a JSON document from the local file system with a `pathlib.Path`.
    """

    document = load_json_document(_json_test_cases_dir / "json-document.json")
    assert document.get("This") == "Is Valid JSON"


def test_loading_json_from_url():
    """
    Ensure we can load a JSON document from the local file system with a `pathlib.Path`.
    """

    with requests_mock.Mocker() as m:
        m.get(
            "http://url/file.json",
            text='{"columns": []}',
        )

        document = load_json_document("http://url/file.json")
        assert isinstance(document.get("columns"), list)


@pytest.fixture(autouse=True)
def dummy_mapped_url():
    map_url_to_file_path["//thisisatestfornickandcharlesons.com"] = (
        APP_ROOT_DIR_PATH / "schema" / "cube-config" / "v1_3" / "schema.json"
    )
    yield None
    del map_url_to_file_path["//thisisatestfornickandcharlesons.com"]


def test_load_local_when_http_request_fails():
    """
    Ensure that a local copy of a document is returned when an http request fails in any
    instance. Most likley due to lack of internet connectivity.
    """

    with session.cache_disabled():
        json_document = load_json_document(
            "https://thisisatestfornickandcharlesons.com"
        )

        expected_document = (
            APP_ROOT_DIR_PATH / "schema" / "cube-config" / "v1_3" / "schema.json"
        )
        with open(expected_document, "r") as f:
            expected = json.load(f)
            assert json_document == expected

# This fixture is a WIP way of possibly using the same fixture for multiple tests instead of duplicating them and changing the input url.
# May not keep it, may improve it further.
@pytest.fixture(autouse=True)
def err_code_dummy_map_url():
    def add_dummy_url(input_url):
        map_url_to_file_path[input_url] = (
        APP_ROOT_DIR_PATH / "schema" / "cube-config" / "v1_3" / "schema.json"
        )
        yield None
        del map_url_to_file_path[input_url]
    return add_dummy_url

def test_load_local_when_bad_status_code(err_code_dummy_map_url):
    """
    Ensures that a local copy of a document is returned when a HTTP request returns a response
     with a 4**/5** status code.
    """
    input_url = "https://purl.org/csv-cubed/qube-config/v1.3X"
    err_code_dummy_map_url("https://purl.org/csv-cubed/qube-config/v1.3X")
    with session.cache_disabled():
        json_document = load_json_document(
            input_url
        )

        expected_document = (
            APP_ROOT_DIR_PATH / "schema" / "cube-config" / "v1_3" / "schema.json"
        )
        with open(expected_document, "r") as f:
            expected = json.load(f)
            assert json_document == expected


if __name__ == "__main__":
    pytest.main()