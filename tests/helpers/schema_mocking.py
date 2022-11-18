"""
Schema Mocking Helpers
----------------------

Helper functions for mocking the schema and templates.
"""
from typing import Optional

import requests_mock
from requests.sessions import Session

from csvcubed.utils.cache import get_url_to_file_path_map


def mock_json_schemas(session: Optional[Session] = None) -> requests_mock.Mocker:

    map_uri_to_file_path = get_url_to_file_path_map()

    mocker = requests_mock.Mocker(session=session, real_http=True)

    for (uri, file_path) in map_uri_to_file_path.items():
        with open(file_path) as f:
            mocker.register_uri(
                "GET",
                uri,
                text=f.read(),
            )

    return mocker
