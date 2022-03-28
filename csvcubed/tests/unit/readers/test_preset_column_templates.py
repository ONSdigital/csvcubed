from requests.exceptions import HTTPError
from copy import deepcopy

import pytest
import requests_mock

from definitions import ROOT_DIR_PATH
from csvcubed.utils.cache import session
from csvcubed.readers.cubeconfig.schema_versions import (
    QubeConfigJsonSchemaVersion,
)
from csvcubed.readers.preconfiguredtemplates import (
    _get_properties_from_template_file,
    _get_template_file_from_template_lookup,
    apply_preconfigured_values_from_template,
)

TEMPLATE_BASE_URL = "https://raw.githubusercontent.com/GSS-Cogs/csvcubed/main/csvcubed/csvcubed/readers/{}/templates/{}"


@pytest.fixture(autouse=True)
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


def test_func_accepts_dict_with_template():
    column_config = {"label": "year", "from_template": "year"}
    apply_preconfigured_values_from_template(
        column_config, QubeConfigJsonSchemaVersion.V1_0.value
    )
    assert (
        column_config.get("column_uri_template")
        == "http://example.com/code-list/year/{+<column_name>}"
    )


def test_func_accepts_dict_without_template():
    column_config = {
        "label": "year",
    }
    column_config_copy = deepcopy(column_config)
    apply_preconfigured_values_from_template(
        column_config, QubeConfigJsonSchemaVersion.V1_0.value
    )
    assert column_config == column_config_copy


def test_from_template_removed_from_column_config():
    column_config = {"label": "year", "from_template": "year"}
    apply_preconfigured_values_from_template(
        column_config, QubeConfigJsonSchemaVersion.V1_0.value
    )
    assert (
        column_config.get("column_uri_template")
        == "http://example.com/code-list/year/{+<column_name>}"
    )
    assert "from_template" not in column_config


def test_dict_is_exactly_same_as_fetched_template():

    column_config = {"from_template": "nuts geography"}
    apply_preconfigured_values_from_template(
        column_config, QubeConfigJsonSchemaVersion.V1_0.value
    )
    assert column_config.get("column_uri_template") == "http://....../{+<column_name>}"
    assert "from_template" not in column_config
    assert column_config["type"] == "dimension"
    assert column_config["from_existing"] == "...."
    assert column_config["label"] == "NUTSgeography"
    assert column_config["column_uri_template"] == "http://....../{+<column_name>}"


def test_ons_geographies_template_is_fetched():
    column_config = {"from_template": "ons geographies"}
    apply_preconfigured_values_from_template(
        column_config, QubeConfigJsonSchemaVersion.V1_0.value
    )
    assert column_config.get("column_uri_template") == "http://....../{+<column_name>}"
    assert "from_template" not in column_config
    assert column_config["type"] == "dimension"
    assert column_config["from_existing"] == "...."
    assert column_config["label"] == "ONSgeographies"
    assert column_config["column_uri_template"] == "http://....../{+<column_name>}"


def test_raise_error_works_for_none_existing_template_lookup_path():
    version_module_path = QubeConfigJsonSchemaVersion.V1_0.value
    template_lookup_url = TEMPLATE_BASE_URL.format(
        version_module_path, "preset_column_config.json"
    )
    with pytest.raises(HTTPError) as excinfo:
        _get_template_file_from_template_lookup("year", "vv2_0")
        assert f"Unable to get from url {template_lookup_url}. Status code:" in str(
            excinfo
        )


def test_raise_error_works_for_none_existing_template_path():
    version_module_path = QubeConfigJsonSchemaVersion.V1_0.value
    template_url = TEMPLATE_BASE_URL.format(version_module_path, "year.json")
    with pytest.raises(HTTPError) as excinfo:
        _get_properties_from_template_file("year.json", "vv2_0")
        assert f"Unable to get from url {template_url}. Status code:" in str(excinfo)


def test_exception_is_raised_when_given_wrong_template_file_path():
    column_config = {"from_template": "this_doesn't_exist"}
    with pytest.raises(Exception) as excinfo:
        apply_preconfigured_values_from_template(
            column_config, QubeConfigJsonSchemaVersion.V1_0.value
        )
        assert "Couldn't find template your looking for." in str(excinfo)


if __name__ == "__main__":
    pytest.main()
