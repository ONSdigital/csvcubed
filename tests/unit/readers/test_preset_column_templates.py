from copy import deepcopy

import pytest
from requests.exceptions import HTTPError
from csvcubed.definitions import APP_ROOT_DIR_PATH
from csvcubed.utils.cache import map_url_to_file_path, session

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


@pytest.fixture()
def dummy_mapped_url():
    """
    This fixture is used to enable some tests to pass "bad input" URLs without causing an error
    due to a corresponding local file path not existing. It maps the URLs used in those tests to
    a file path that is known to exist. This allows connection errors and other such exceptions
    to happen in a testing scenario.
    """
    # Add test URL to dictionary when ready to use fixture
    test_dictionary = {}
    map_url_to_file_path.update(test_dictionary)
    import logging

    _logger = logging.getLogger(__name__)
    _logger.debug(map_url_to_file_path)
    yield None
    [map_url_to_file_path.pop(key) for key in list(test_dictionary.keys())]
    _logger.debug(map_url_to_file_path)


# Add fixture name to test when ready to use it
def test_get_template_file_when_http_request_fails():
    """
    todo: add desc
    """
    with session.cache_disabled():
        template_url = "//raw.githubusercontent.com/GSS-Cogs/csvcubed/main/src/csvcubed/readers/cubeconfig/v1_0/templates/calendar-hour.json"
        # template_file = _get_template_file_from_template_lookup(template_url)
        template_json = _get_properties_from_template_file(template_url)
        assert template_json == True


if __name__ == "__main__":
    pytest.main()
