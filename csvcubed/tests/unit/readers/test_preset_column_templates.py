import pytest

from requests.exceptions import HTTPError
from copy import deepcopy

from csvcubed.readers.preconfiguredtemplates import(
     _get_propeties_from_template_file, 
     _get_template_file_from_template_lookup, 
     apply_preconfigured_values_from_template,
)
from csvcubed.readers.vnum import JsonSchemaVersion

def test_func_accepts_dict_with_template():
    column_config = {
        "label" : "year",
        "from_template" : "year"
    }
    apply_preconfigured_values_from_template(column_config, JsonSchemaVersion.v1_0.value)
    assert column_config.get("column_uri_template") == "http://....../{+<column_name>}"

def test_func_accepts_dict_without_template():
    column_config = {
        "label" : "year",
    }
    column_config_copy = deepcopy(column_config)
    apply_preconfigured_values_from_template(column_config, JsonSchemaVersion.v1_0.value)
    assert column_config == column_config_copy

def test_from_template_removed_from_column_config():
    column_config = {
        "label" : "year",
        "from_template" : "year"
    }
    apply_preconfigured_values_from_template(column_config, JsonSchemaVersion.v1_0.value)
    assert column_config.get("column_uri_template") == "http://....../{+<column_name>}"
    assert "from_template" not in column_config

def test_dict_is_exactly_same_as_fetched_template():
    column_config = {
        "from_template" : "nuts geography"
    }
    apply_preconfigured_values_from_template(column_config, JsonSchemaVersion.v1_0.value)
    assert column_config.get("column_uri_template") == "http://....../{+<column_name>}"
    assert "from_template" not in column_config
    assert column_config["type"] == "dimension"
    assert column_config["from_existing"] == "...."
    assert column_config["label"] == "NUTSgeography"
    assert column_config["column_uri_template"] == "http://....../{+<column_name>}"

def test_ons_geographies_template_is_fetched():
    column_config = {
        "from_template" : "ons geographies"
    }
    apply_preconfigured_values_from_template(column_config, JsonSchemaVersion.v1_0.value)
    assert column_config.get("column_uri_template") == "http://....../{+<column_name>}"
    assert "from_template" not in column_config
    assert column_config["type"] == "dimension"
    assert column_config["from_existing"] == "...."
    assert column_config["label"] == "ONSgeographies"
    assert column_config["column_uri_template"] == "http://....../{+<column_name>}"

def test_raise_error_works_for_none_existing_template_lookup_path():
    try:
        _get_template_file_from_template_lookup("year", "vv2_0")
    except Exception as e:
        assert isinstance(e, HTTPError)

def test_raise_error_works_for_none_existing_template_path():
    try:
        _get_propeties_from_template_file("year.json", "vv2_0")
    except Exception as e:
        assert isinstance(e, HTTPError)


if __name__ == "__main__":
    pytest.main()