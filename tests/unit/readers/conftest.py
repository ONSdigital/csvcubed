import pytest

from csvcubed.utils.cache import session
from tests.helpers.schema_mocking import mock_json_schemas


@pytest.fixture(scope="package", autouse=True)
def mock_json_schemas_fixture():
    """
    Fixture which mocks the HTTP responses of the JSON schema files for testing.
    """
    with session.cache_disabled(), mock_json_schemas(session):
        yield session
