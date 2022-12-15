import pytest
import requests_mock
import json

from tests.unit.test_baseunit import get_test_cases_dir
from csvcubed.utils.json import load_json_document
from csvcubed.utils.cache import session
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


def test_load_local_when_http_request_fails(dummy_mapped_url):
    """
    Ensure that a local copy of a document is returned when an http request fails and does not
    return a response at all. Most likely due to lack of internet connectivity.
    """

    with session.cache_disabled():
        json_document = load_json_document(
            "https://thisinputurlwillcauseanerror.com"
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


def test_connection_error_for_bad_url():
    """
    Ensures a FileNotFound error is successfully produced when a request is made with load_json_document
    using a non-existent URL as input, meaning no response is returned and no local copy can be found.
    """
    
    with pytest.raises(FileNotFoundError) as err:
        with session.cache_disabled():
            json_document = load_json_document("https://thistesturlwillnotproducearesponse.org")

    assert str(err.value) == 'URL https://thistesturlwillnotproducearesponse.org/ did not produce a response and a local copy could not be found at the corresponding mapped path.'

def test_connection_error_url():
    """
    Ensures a FileNotFound exception is successfully produced when a request is made with load_json_document
    which causes a response to be returned, but with a client or server error status code and no local copy to be found.
    """
    
    with pytest.raises(FileNotFoundError) as err:
        with session.cache_disabled():
            json_document = load_json_document("https://purl.org/csv-cubed/qube-config/produces404")

    assert str(err.value) == 'URL https://purl.org/csv-cubed/qube-config/produces404 produced a invalid response and a local copy could not be found at the corresponding mapped path.'


if __name__ == "__main__":
    pytest.main()