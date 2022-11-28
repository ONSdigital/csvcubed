import pytest
import requests_mock

from tests.unit.test_baseunit import get_test_cases_dir
from csvcubed.utils.json import load_json_document

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


def test_load_local_when_http_request_fails():
    """
    Ensure that a local copy of a document is returned when an http request fails in any
    instance. Most likley due to lack of internet connectivity.
    """
    from csvcubed.utils.cache import session
    with session.cache_disabled():  
        document = load_json_document("https://purl.org/csv-cubed/qube-config/v1.3X")
        assert document == True


if __name__ == "__main__":
    pytest.main()
