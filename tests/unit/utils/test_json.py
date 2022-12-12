import pytest
import requests_mock
import json
from typing import List

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


@pytest.fixture()
def dummy_mapped_url():
    """
    This fixture is used to enable some tests to pass "bad input" URLs without causing an error
    due to a corresponding local file path not existing. It maps the URLs used in those tests to
    a file path that is known to exist. This allows connection errors and other such exceptions
    to happen in a testing scenario.
    """
    test_dictionary = {"//thisisatestfornickandcharlesons.com" : APP_ROOT_DIR_PATH / "schema" / "cube-config" / "v1_3" / "schema.json",
                    "//purl.org/csv-cubed/qube-config/badinput" : APP_ROOT_DIR_PATH / "schema" / "cube-config" / "v1_3" / "schema.json"}
    map_url_to_file_path.update(test_dictionary)
    import logging
    _logger = logging.getLogger(__name__)
    _logger.debug(map_url_to_file_path)
    yield None
    #[a.pop(key) for key in ['key1', 'key3']]
    [map_url_to_file_path.pop(key) for key in list(test_dictionary.keys())]
    _logger.debug(map_url_to_file_path)


def test_load_local_when_http_request_fails(dummy_mapped_url):
    """
    Ensure that a local copy of a document is returned when an http request fails in any
    instance. Most likely due to lack of internet connectivity.
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


def test_load_local_when_bad_status_code(dummy_mapped_url):
    """
    Ensures that a local copy of a document is returned when a HTTP request returns a response
     with a 4**/5** status code. (In this case 404)
    """
    with session.cache_disabled():
        json_document = load_json_document(
            "https://purl.org/csv-cubed/qube-config/badinput"
        )

        expected_document = (
            APP_ROOT_DIR_PATH / "schema" / "cube-config" / "v1_3" / "schema.json"
        )
        with open(expected_document, "r") as f:
            expected = json.load(f)
            assert json_document == expected


#Unsure if this test will be implemented as it may be unnecessary, map function is implicitly shown to work in previous tests.
def test_url_to_path_map():
    """
    Ensures that a given URL is properly mapped to a corresponding file path for rerieving
    files (e.g. cube config files) from local storage.
    """


def test_connection_error_for_bad_url():
    """
    Ensures a FileNotFound error is successfully produced when a request is made with load_json_document
    using a non-existent URL as input, meaning no response is returned and no local copy can be found.
    """
    
    with pytest.raises(FileNotFoundError) as err:
        with session.cache_disabled():
            json_document = load_json_document("https://thistesturlwillnotproducearesponse.org")

    assert str(err.value) == 'URL https://thistesturlwillnotproducearesponse.org/ did not produce a response and a local copy could not be found at the corresponding mapped path.'

def test_connection_error__url():
    """
    Ensures a FileNotFound exception is successfully produced when a request is made with load_json_document
    which causes a response to be returned, but with a client or server error status code
    (in this case 404 due to valid endpoint but non-existent resource requested) and no local copy to be found.
    """
    
    with pytest.raises(FileNotFoundError) as err:
        with session.cache_disabled():
            json_document = load_json_document("https://purl.org/csv-cubed/qube-config/produces404")

    assert str(err.value) == 'URL https://purl.org/csv-cubed/qube-config/produces404 produced a invalid response and a local copy could not be found at the corresponding mapped path.'


if __name__ == "__main__":
    pytest.main()