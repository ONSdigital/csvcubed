import pytest
import requests_mock

from csvcubed.utils.cache import session
from csvcubed.definitions import APP_ROOT_DIR_PATH


@pytest.fixture(scope="package", autouse=True)
def mock_http_session_qube_config_schema():
    """
    Fixture which mocks the HTTP responses of the JSON qube-config schema file for testing.
    """

    with session.cache_disabled(), requests_mock.Mocker(
        session=session, real_http=True
    ) as mocker:
        schema_path = (
            APP_ROOT_DIR_PATH / "schema" / "cube-config" / "v1_0" / "schema.json"
        )

        with open(schema_path) as f:
            mocker.register_uri(
                "GET",
                "//purl.org/csv-cubed/qube-config/v1.0",
                text=f.read(),
            )

        yield session
