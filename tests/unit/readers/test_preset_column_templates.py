from copy import deepcopy

import pytest
from requests.exceptions import HTTPError

from csvcubed.readers.preconfiguredtemplates import (
    TEMPLATE_BASE_URL,
    _get_properties_from_template_file,
    _get_template_file_from_template_lookup,
    apply_preconfigured_values_from_template,
)


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
    with pytest.raises(HTTPError) as excinfo:
        _get_properties_from_template_file("year.json")
        assert f"Unable to get from url {template_url}. Status code:" in str(excinfo)


def test_exception_is_raised_when_given_wrong_template_file_path():
    column_config = {"from_template": "this_doesn't_exist"}
    with pytest.raises(Exception) as excinfo:
        apply_preconfigured_values_from_template(column_config)
        assert "Couldn't find template your looking for." in str(excinfo)


def test_get_template_file_when_http_request_fails():
    """
    todo: add desc
    """
    template_url = "//raw.githubusercontent.com/GSS-Cogs/csvcubed/main/src/csvcubed/readers/cubeconfig/v1_0/templates/calendar-hour.json"
    # template_file = _get_template_file_from_template_lookup(template_url)
    template_json = _get_properties_from_template_file(template_url)
    assert template_json == True


if __name__ == "__main__":
    pytest.main()
