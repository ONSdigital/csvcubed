"""
Schema Mocking Helpers
----------------------

Helper functions for mocking the schema and templates.
"""
from typing import Optional

import requests_mock
from requests.sessions import Session

from csvcubed.definitions import APP_ROOT_DIR_PATH


def mock_json_schemas(session: Optional[Session] = None) -> requests_mock.Mocker:
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
        "//purl.org/csv-cubed/qube-config/v1": APP_ROOT_DIR_PATH
        / "schema"
        / "cube-config"
        / "v1_3"
        / "schema.json",  # v1 defaults to latest minor version of v1.*.
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
        "//purl.org/csv-cubed/code-list-config/v1": APP_ROOT_DIR_PATH
        / "schema"
        / "codelist-config"
        / "v1_1"
        / "schema.json",  # v1 defaults to latest minor version of v1.*.
    }

    templates_dir = APP_ROOT_DIR_PATH / "readers" / "cubeconfig" / "v1_0" / "templates"

    template_files = templates_dir.rglob("**/*.json*")

    if not any(template_files):
        raise ValueError(f"Couldn't find template files in {templates_dir}.")

    for template_file in template_files:
        relative_file_path = str(template_file.relative_to(templates_dir))
        uri = (
            "//raw.githubusercontent.com/GSS-Cogs/csvcubed/main/src/csvcubed/readers/cubeconfig/v1_0/templates/"
            + relative_file_path
        )
        map_uri_to_file_path[uri] = template_file

    mocker = requests_mock.Mocker(session=session, real_http=True)

    for (uri, file_path) in map_uri_to_file_path.items():
        with open(file_path) as f:
            mocker.register_uri(
                "GET",
                uri,
                text=f.read(),
            )

    return mocker
