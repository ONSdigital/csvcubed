# this script will test the validationmodel features
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pytest

from csvcubed.models.validatedmodel import ValidatedModel, ValidationFunction
from csvcubed.utils.validations import (
    validate_file_path,
    validate_float_type,
    validate_int_type,
    validate_list,
    validate_optional,
    validate_str_type,
    validate_uri,
)
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "models"


@dataclass
class TestClass(ValidatedModel):
    """This the test class that will be used in the tests below"""

    str_test_variable: str
    int_test_variable: int
    float_test_variable: float
    list_test_variable: List[str]
    # path_test_variable: Path
    test_uri: Optional[str] = None

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {
            "str_test_variable": validate_str_type,
            "int_test_variable": validate_int_type,
            "float_test_variable": validate_float_type,
            "list_test_variable": validate_list(validate_str_type),
            # "path_test_variable": validate_file_path,
            "test_uri": validate_optional(validate_uri),
        }


# TODO Windows/Unix paths
def test_validate_int_type_incorrect():
    """
    This test will validate if the class has been instanciated with a variable that was expecting an integer,
    but it was provided with a non int type variable.
    """

    test_instance = TestClass(
        str_test_variable="test",
        int_test_variable="test",
        float_test_variable=3.14,
        list_test_variable=[],
    )

    result = test_instance.validate()

    assert len(result) == 1
    assert (
        result[0].message
        == "This variable should be a integer value, check the following variable:"
    )
    assert result[0].property_name == "int_test_variable"


def test_validate_int_type_correct():
    """This test will check if the class with the correct argument types will pass the validation"""

    test_instance = TestClass(
        str_test_variable="test",
        int_test_variable=5,
        float_test_variable=3.14,
        list_test_variable=[],
    )

    result = test_instance.validate()

    assert len(result) == 0


def test_validate_str_type_incorrect():
    """
    This test will validate if the class has been instanciated with a variable that was expecting an string,
    but it was provided with a non string type variable.
    """

    test_instance = TestClass(
        str_test_variable=5,
        int_test_variable=8,
        float_test_variable=3.14,
        list_test_variable=[],
    )

    result = test_instance.validate()

    assert len(result) == 1
    assert (
        result[0].message
        == "This variable should be a string value, check the following variable:"
    )
    assert result[0].property_name == "str_test_variable"


def test_validate_str_type_correct():
    """This test will check if the class with the correct argument types will pass the validation"""

    test_instance = TestClass(
        str_test_variable="test",
        int_test_variable=8,
        float_test_variable=3.14,
        list_test_variable=[],
    )

    result = test_instance.validate()

    assert len(result) == 0


def test_validate_list_type_incorrect():
    """
    This test will validate if the class has been instanciated with a variable that was expecting an List of string,
    but it was provided with a non List type variable, also a List with a non string type item.
    """

    test_instance = TestClass(
        str_test_variable="test",
        int_test_variable=8,
        float_test_variable=3.14,
        list_test_variable="nope",
    )

    result = test_instance.validate()

    assert len(result) == 1
    assert (
        result[0].message
        == "This variable should be a list, check the following variable:"
    )
    assert result[0].property_name == "list_test_variable"

    my_list = ["Something", 8, "Something Else"]

    test_instance = TestClass("test", 8, 3.14, my_list)

    result = test_instance.validate()

    assert len(result) == 1
    assert (
        result[0].message
        == "This variable should be a string value, check the following variable:"
    )
    assert result[0].property_name == "list_test_variable"


def test_validate_list_type_correct():
    """This test will check if the class with the correct argument types will pass the validation"""

    my_list: List[str] = ["test", "test2"]
    test_instance = TestClass(
        str_test_variable="test",
        int_test_variable=8,
        float_test_variable=3.14,
        list_test_variable=my_list,
    )

    result = test_instance.validate()

    assert len(result) == 0


def test_validate_uri_incorrect():
    """This test will check if the string variable that should be a uri is in fact a uri."""

    my_list: List[str] = ["test", "test2"]
    test_instance = TestClass(
        str_test_variable="test",
        int_test_variable=8,
        float_test_variable=3.14,
        list_test_variable=my_list,
        test_uri="whatever",
    )

    result = test_instance.validate()

    assert len(result) == 1
    assert result[0].message == "This variable is not a valid uri."


def test_validate_uri_none_correct():
    """This test will check is the optional variable(by default None) is a None and will pass the validation"""
    my_list: List[str] = ["test", "test2"]
    test_instance = TestClass(
        str_test_variable="test",
        int_test_variable=8,
        float_test_variable=3.14,
        list_test_variable=my_list,
    )

    result = test_instance.validate()

    assert len(result) == 0


def test_validate_uri_correct():
    """This test will check if the class with the correct argument types will pass the validation"""
    my_list: List[str] = ["test", "test2"]
    test_instance = TestClass(
        str_test_variable="test",
        int_test_variable=8,
        float_test_variable=3.14,
        list_test_variable=my_list,
        test_uri="http://example.com",
    )

    result = test_instance.validate()

    assert len(result) == 0


# TODO NaN, +/-infinity
def test_validate_float_type_incorrect():
    """
    This test will validate if the class has been instanciated with a variable that was expecting an float,
    but it was provided with a non float type variable.
    """

    test_instance = TestClass(
        str_test_variable="test",
        int_test_variable=5,
        float_test_variable="test",
        list_test_variable=[],
    )

    result = test_instance.validate()

    assert len(result) == 1
    assert (
        result[0].message
        == "This variable should be a float value, check the following variable:"
    )
    assert result[0].property_name == "float_test_variable"


def test_validate_float_type_correct():
    """This test will check if the class with the correct argument types will pass the validation"""

    test_instance = TestClass(
        str_test_variable="test",
        int_test_variable=5,
        float_test_variable=3.14,
        list_test_variable=[],
    )

    result = test_instance.validate()

    assert len(result) == 0


def test_validate_file_path_not_exists():
    """ """
    test_instance = TestClass(
        str_test_variable="test",
        int_test_variable=5,
        float_test_variable=3.14,
        list_test_variable=[],
    )


if __name__ == "__main__":
    pytest.main()
