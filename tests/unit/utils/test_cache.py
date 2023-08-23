import json

import pytest

from csvcubed.definitions import APP_ROOT_DIR_PATH
from csvcubed.utils.cache import session
from csvcubed.utils.json import load_json_document


def test_load_local_when_http_request_fails(dummy_mapped_url):
    """
    Ensure that a local copy of a document is returned when an http request fails and does not
    return a response at all. Most likely due to lack of internet connectivity.
    """

    with session.cache_disabled():
        json_document = load_json_document("https://thisinputurlwillcauseanerror.com")

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
            _ = load_json_document("https://thistesturlwillnotproducearesponse.org")

    assert (
        str(err.value)
        == "URL 'https://thistesturlwillnotproducearesponse.org/' did not produce a response and a local copy could not be found."
    )


def test_connection_error_url():
    """
    Ensures a FileNotFound exception is successfully produced when a request is made with load_json_document
    which causes a response to be returned, but with a client or server error status code and no local copy to be found.
    """

    with pytest.raises(FileNotFoundError) as err:
        with session.cache_disabled():
            _ = load_json_document("https://purl.org/csv-cubed/qube-config/produces404")

    assert (
        str(err.value)
        == "URL 'https://purl.archive.org/csv-cubed/qube-config/produces404' produced a invalid response and a local copy could not be found."
    )


if __name__ == "__main__":
    pytest.main()
