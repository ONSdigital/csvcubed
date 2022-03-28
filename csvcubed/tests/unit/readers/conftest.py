import pytest
import requests_mock

from csvcubed.utils.cache import session
from definitions import ROOT_DIR_PATH


@pytest.fixture(autouse=True, scope="package")
def mock_http_session():
    """
    Fixture which mocks the HTTP responses of the JSON template files for testing.
    """

    with session.cache_disabled(), requests_mock.Mocker(
        session=session, real_http=True
    ) as mocker:
        templates_dir = (
            ROOT_DIR_PATH / "csvcubed" / "readers" / "cubeconfig" / "v1_0" / "templates"
        )

        for template_file in templates_dir.rglob("**/*.json"):
            relative_file_path = str(template_file.relative_to(templates_dir))
            with open(template_file) as f:
                mocker.register_uri(
                    "GET",
                    "//raw.githubusercontent.com/GSS-Cogs/csvcubed/main/csvcubed/csvcubed/readers/v1_0/templates/"
                    + relative_file_path,
                    text=f.read(),
                )

        yield session
