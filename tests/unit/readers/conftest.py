import pytest
import requests_mock

from csvcubed.utils.cache import session
from csvcubed.definitions import APP_ROOT_DIR_PATH


@pytest.fixture(autouse=True, scope="package")
def mock_http_session():
    """
    Fixture which mocks the HTTP responses of the JSON template files for testing.
    """

    with session.cache_disabled(), requests_mock.Mocker(
        session=session, real_http=True
    ) as mocker:
        templates_dir = (
            APP_ROOT_DIR_PATH / "readers" / "cubeconfig" / "v1_0" / "templates"
        )

        template_files = templates_dir.rglob("**/*.json*")

        if not any(template_files):
            raise ValueError(f"Couldn't find template files in {templates_dir}.")

        for template_file in template_files:
            relative_file_path = str(template_file.relative_to(templates_dir))
            with open(template_file) as f:
                mocker.register_uri(
                    "GET",
                    "//raw.githubusercontent.com/GSS-Cogs/csvcubed/main/src/csvcubed/readers/cubeconfig/v1_0/templates/"
                    + relative_file_path,
                    text=f.read(),
                )

        yield session


@pytest.fixture(scope="package", autouse=True)
def mock_json_schemas():
    """
    Fixture which mocks the HTTP responses of the JSON schema files for testing.
    """
    map_uri_to_file_path = {
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
    }

    with session.cache_disabled(), requests_mock.Mocker(
        session=session, real_http=True
    ) as mocker:
        for (uri, file_path) in map_uri_to_file_path.items():
            with open(file_path) as f:
                mocker.register_uri(
                    "GET",
                    uri,
                    text=f.read(),
                )

        yield session
