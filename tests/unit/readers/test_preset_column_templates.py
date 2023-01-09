import json
from copy import deepcopy

import pytest

from csvcubed.definitions import APP_ROOT_DIR_PATH
from csvcubed.readers.preconfiguredtemplates import (
    TEMPLATE_BASE_URL, _get_properties_from_template_file,
    _get_template_file_from_template_lookup,
    apply_preconfigured_values_from_template)


def test_func_accepts_dict_with_template():
    column_config = {"label": "year", "from_template": "year"}
    apply_preconfigured_values_from_template(column_config, "year")
    assert (
        column_config.get("cell_uri_template")
        == "http://reference.data.gov.uk/id/year/{+year}"
    )


def test_func_accepts_dict_without_template():
    column_config = {
        "label": "year",
    }
    column_config_copy = deepcopy(column_config)
    apply_preconfigured_values_from_template(column_config, "year")
    assert column_config == column_config_copy


def test_from_template_removed_from_column_config():
    column_config = {"label": "year", "from_template": "year"}
    apply_preconfigured_values_from_template(column_config, "year")
    assert (
        column_config.get("cell_uri_template")
        == "http://reference.data.gov.uk/id/year/{+year}"
    )
    assert "from_template" not in column_config


def test_raise_error_works_for_none_existing_template_lookup_path():
    template_lookup_url = f"{TEMPLATE_BASE_URL}/preset_column_config.json"
    with pytest.raises(Exception) as excinfo:
        _get_template_file_from_template_lookup("year_none_existing")
        assert f"Unable to get from url {template_lookup_url}. Status code:" in str(
            excinfo
        )


def test_raise_error_works_for_none_existing_template_path():
    template_url = f"{TEMPLATE_BASE_URL}/year.json"
    with pytest.raises(FileNotFoundError) as excinfo:
        _get_properties_from_template_file("year.json")
        assert f"Unable to get from url {template_url}. Status code:" in str(excinfo)


def test_exception_is_raised_when_given_wrong_template_file_path():
    column_config = {"from_template": "this_doesn't_exist"}
    with pytest.raises(Exception) as excinfo:
        apply_preconfigured_values_from_template(column_config)
        assert "Couldn't find template your looking for." in str(excinfo)


def test_get_template_file_when_bad_status_code(dummy_mapped_url):
    """
    Ensures that a template file can still be retrieved locally when the request from load_json_document
    returns a response with an error status code, in this case by giving a URL to a non-existent resource.
    Note that since the URL prefix for templates is "hard-coded", it has to be as seen in the test,
    meaning that making a test for not getting a response at all is unnecessary/impossible.
    """
    expected_template_json = (
        APP_ROOT_DIR_PATH
        / "readers"
        / "cubeconfig"
        / "v1_0"
        / "templates"
        / "calendar-year.json"
    )

    template_url_suffix = "calendar-hourx.json"
    template_json = _get_properties_from_template_file(template_url_suffix)

    with open(expected_template_json, "r") as f:
        expected = json.load(f)
        assert template_json == expected


if __name__ == "__main__":
    pytest.main()
