# this script will test the validationmodel features
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

import pytest
from rdflib.term import Identifier

from csvcubed.models.cube.qb.components.arbitraryrdf import TripleFragmentBase
from csvcubed.models.cube.qb.components.unit import NewQbUnit, QbUnit
from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.models.validatedmodel import (
    ValidatedModel,
    ValidationFunction,
    Validations,
)
from csvcubed.models.validationerror import ValidateModelPropertiesError
from csvcubed.utils import validations as v
from csvcubed.utils.validations import (
    boolean,
    validate_file,
    validate_float_type,
    validate_int_type,
    validate_list,
    validate_optional,
    validate_str_type,
    validate_uri,
)
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "cli" / "inspect"


class TestEnum(Enum):
    First_Value = (0,)


class OtherTestEnum(Enum):
    First_Value = (0,)


@dataclass
class OtherTestClass(ValidatedModel):
    str_test_variable_2: str

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {"str_test_variable_2": validate_str_type}


@dataclass
class TestClass(ValidatedModel):
    """This the test class that will be used in the tests below"""

    str_test_variable: str = "Hello, World"
    int_test_variable: int = 1
    float_test_variable: float = 1.0
    list_test_variable: List[str] = field(default_factory=list)
    date_test_variable: Optional[date] = None
    date_time_test_variable: Optional[datetime] = None
    path_test_variable: Optional[Path] = None
    test_uri: Optional[str] = None
    test_enum_value: Optional[TestEnum] = None
    test_any_of_value: Union[str, int, None] = None
    test_validated_model_class: Optional[OtherTestClass] = None
    test_data_type: Optional[str] = None
    test_validate_instance_of: Optional[Identifier] = None
    bool_test_variable: Optional[bool] = True

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {
            "str_test_variable": validate_str_type,
            "int_test_variable": validate_int_type,
            "bool_test_variable": boolean,
            "float_test_variable": validate_float_type,
            "list_test_variable": validate_list(validate_str_type),
            "path_test_variable": validate_optional(validate_file),
            "date_test_variable": validate_optional(v.is_instance_of(date)),
            "date_time_test_variable": validate_optional(v.is_instance_of(datetime)),
            "test_uri": validate_optional(validate_uri),
            "test_enum_value": validate_optional(v.enum(TestEnum)),
            "test_any_of_value": validate_optional(
                v.any_of(validate_str_type, validate_int_type)
            ),
            "test_validated_model_class": validate_optional(
                v.validated_model(OtherTestClass)
            ),
            "test_data_type": validate_optional(v.any_of(v.data_type, validate_uri)),
            "test_validate_instance_of": validate_optional(
                v.is_instance_of(Identifier)
            ),
        }


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
        str_test_variable="test", int_test_variable=5, float_test_variable=3.14
    )

    result = test_instance.validate()

    assert len(result) == 0


def test_validate_str_type_incorrect():
    """
    This test will validate if the class has been instanciated with a variable that was expecting an string,
    but it was provided with a non string type variable.
    """

    test_instance = TestClass(
        str_test_variable=5, int_test_variable=8, float_test_variable=3.14
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
        str_test_variable="test", int_test_variable=8, float_test_variable=3.14
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


def test_validate_float_type_incorrect():
    """
    This test will validate if the class has been instanciated with a variable that was expecting an float,
    but it was provided with a non float type variable.
    """

    test_instance = TestClass(
        str_test_variable="test", int_test_variable=5, float_test_variable="test"
    )

    result = test_instance.validate()

    assert len(result) == 1
    assert (
        result[0].message
        == "This variable should be a float value, check the following variable:"
    )
    assert result[0].property_name == "float_test_variable"


def test_validate_float_type_nan_incorrect():
    """
    This test will validate if the class has been instanciated with a variable that was expecting an float,
    but it was provided with a float("nan") instead.
    """

    test_instance = TestClass(
        str_test_variable="test", int_test_variable=5, float_test_variable=float("nan")
    )

    result = test_instance.validate()

    assert len(result) == 1
    assert (
        result[0].message
        == "This variable should be a float value but is Not a Number (NaN), check the following variable:"
    )
    assert result[0].property_name == "float_test_variable"


def test_validate_float_type_infinity_incorrect():
    """
    This test will validate if the class has been instanciated with a variable that was expecting an float,
    but it was provided with a float("inf") instead.
    """

    test_instance = TestClass(
        str_test_variable="test", int_test_variable=5, float_test_variable=float("inf")
    )

    result = test_instance.validate()

    assert len(result) == 1
    assert (
        result[0].message
        == "This variable should be a float value but is +-infinity, check the following variable:"
    )
    assert result[0].property_name == "float_test_variable"


def test_validate_float_type_neg_infinity_incorrect():
    """
    This test will validate if the class has been instanciated with a variable that was expecting an float,
    but it was provided with a float("-inf") instead.
    """

    test_instance = TestClass(
        str_test_variable="test", int_test_variable=5, float_test_variable=float("-inf")
    )

    result = test_instance.validate()

    assert len(result) == 1
    assert (
        result[0].message
        == "This variable should be a float value but is +-infinity, check the following variable:"
    )
    assert result[0].property_name == "float_test_variable"


def test_validate_float_type_correct():
    """
    This test will check if the class given the correct arguments (in this case, a float) will be
    validated without any errors being returned.
    """

    test_instance = TestClass(
        str_test_variable="test", int_test_variable=5, float_test_variable=3.14
    )

    result = test_instance.validate()

    assert len(result) == 0


def test_validate_file_exists():
    """
    This test will check if the test class given the correct arguments (in this case, a file path) will be
    successfully validated without returning any errors.
    """
    test_instance = TestClass(
        str_test_variable="test",
        int_test_variable=5,
        float_test_variable=3.14,
        path_test_variable=_test_case_base_dir / "csv_file.csv",
    )

    result = test_instance.validate()

    assert len(result) == 0


def test_validate_file_not_exists():
    """
    This test will validate if the class has been instanciated with a variable that was expecting a file that exists,
    but it was provided with a file that does not exist instead.
    """
    test_instance = TestClass(
        path_test_variable=_test_case_base_dir / "not_a_csv_file.csv",
    )

    result = test_instance.validate()

    assert len(result) == 1
    assert (
        result[0].message == "This file does not exist, check the following variable:"
    )
    assert result[0].property_name == "path_test_variable"


def test_validate_file_not_a_path():
    """
    This test will validate if the class has been instanciated with a variable that was expecting a valid file path,
    but it was provided with an invalid file path instead.
    """
    test_instance = TestClass(
        path_test_variable="test",
    )

    result = test_instance.validate()

    assert len(result) == 1
    assert (
        result[0].message
        == "This is not a valid file path, check the following variable:"
    )
    assert result[0].property_name == "path_test_variable"


def test_validate_datetime_correct():
    """
    This test checks whether the test class given the correct argument (in this case, a datetime object)
    will be validated successfully without errors.
    """
    test_instance = TestClass(
        date_test_variable=datetime.today(),
    )

    result = test_instance.validate()

    assert len(result) == 0


def test_validate_date_correct():
    """
    This test checks whether the test class given the correct argument (in this case, a date object)
    will be validated successfully without errors.
    """
    test_instance = TestClass(
        date_test_variable=date.today(),
    )

    result = test_instance.validate()

    assert len(result) == 0


def test_validate_date_incorrect():
    """
    This test checks whether the test class given an incorrect argument (in this case, a string object
    when a date is expected) will be validated successfully and return the expected error.
    """
    test_instance = TestClass(
        date_test_variable="test",
    )

    result = test_instance.validate()

    assert len(result) == 1
    assert (
        result[0].message
        == "Value 'test' was not an instance of the expected type 'date'."
    )
    assert result[0].property_name == "date_test_variable"


def test_validate_enum_correct():
    """
    This test checks whether a test class given the correct expected argument (in this case,
    an object of type TestEnum defined specifically for these tests) is successfully
    validated with no errors.
    """
    test_instance = TestClass(test_enum_value=TestEnum.First_Value)

    errors = test_instance.validate()

    assert not any(errors)


def test_validate_enum_incorrect():
    """
    Checks whether a test class given an incorrect expected argument, when an argument of type TestEnum
    is expected, is validated and returns errors.
    """
    test_instance = TestClass(test_enum_value=OtherTestEnum.First_Value)

    errors = test_instance.validate()

    assert any(errors)


def test_validate_any_of_correct():
    """
    Checks whether a class given correct arguments, when any objects of type string or int are
    accepted, successfully validates and returns no errors.
    """
    test_instance = TestClass(test_any_of_value="hi")

    errors = test_instance.validate()

    assert not any(errors)

    test_instance = TestClass(test_any_of_value=3)

    errors = test_instance.validate()

    assert not any(errors)


def test_validate_any_of_incorrect():
    """
    Checks whether a class given incorrect arguments (in this case a float) when any_of
    only strings or ints are accepted, validates and returns errors.
    """
    test_instance = TestClass(test_any_of_value=3.65)

    errors = test_instance.validate()

    assert any(errors)


def test_validated_model_validation_correct():
    """
    Tests whether a class using validated_model to validate an object of a type which inherits from the
    ValidatedModel class works successfully without returning any errors.
    """
    test_instance = TestClass(
        test_validated_model_class=OtherTestClass(str_test_variable_2="This is valid")
    )

    errors = test_instance.validate()

    assert not any(errors)


def test_validated_model_validation_incorrect_type():
    """
    Tests whether a class using validated_model to validate an object of a type which inherits from the
    ValidatedModel class returns errors when given an incorrect object type.
    """
    test_instance = TestClass(
        test_validated_model_class=OtherTestClass(str_test_variable_2=3.14)
    )

    errors = test_instance.validate()

    assert any(errors)


def test_validated_model_is_not_inherited():
    """
    Tests whether attempting to use validated_model validation on an object which does not inherit from
    the VaidatedModel class returns errors as expected.
    """
    test_instance = TestClass(
        test_validated_model_class="This is not an instance of the right class."
    )

    errors = test_instance.validate()

    assert any(errors)


@dataclass
class WholeObjectValidationsTestClass(ValidatedModel):
    """
    This is the class that will be used to test whole-object validation.
    """

    test_validate_str: str
    test_validate_int: int

    def _get_validations(self) -> Union[Validations, Dict[str, ValidationFunction]]:
        return Validations(
            individual_property_validations={
                "test_validate_str": validate_str_type,
                "test_validate_int": validate_int_type,
            },
            whole_object_validations=[self._whole_object_validation],
        )

    @staticmethod
    def _whole_object_validation(the_instance) -> List[ValidateModelPropertiesError]:
        errors: List[ValidateModelPropertiesError] = []
        if the_instance.test_validate_str.lower() == "positive":
            if the_instance.test_validate_int < 0:
                errors.append(
                    ValidateModelPropertiesError(
                        "Expected a positive integer", "Whole Object"
                    )
                )
        else:
            # Negative
            if the_instance.test_validate_int > 0:
                errors.append(
                    ValidateModelPropertiesError(
                        "Expected a negative integer", "Whole Object"
                    )
                )
        return errors


def test_whole_object_validation_correct():
    """
    Ensures that whole-object validation applied to an object with correctly defined properties
    succeeds and returns no errors.
    """
    test_instance = WholeObjectValidationsTestClass(
        test_validate_str="positive", test_validate_int=2
    )
    errors = test_instance.validate()
    assert not any(errors)


def test_whole_object_validation_incorrect():
    """
    Ensures that whole-object validation applied to an object with incorrectly defined property values
    successfully returns errors as expected.
    """
    test_instance = WholeObjectValidationsTestClass(
        test_validate_str="positive", test_validate_int=-2
    )
    errors = test_instance.validate()
    assert any(errors)


def test_validate_is_instance_of_correct():
    """
    Tests that the is_instance_of function successfully validates an object of a type that
    does not inherit from ValidationModel and returns no errors.
    """
    test_instance = TestClass(test_validate_instance_of=Identifier("hi"))
    errors = test_instance.validate()
    assert not any(errors)


def test_validate_is_instance_of_incorrect():
    """
    Ensures the is_instance_of function validates an object of a type that does not inherit
    from ValidationModel and returns errors correctly when expected. (Type is incorrect)
    """
    test_instance = TestClass(test_validate_instance_of="Woof")
    errors = test_instance.validate()
    assert any(errors)


def test_validate_data_type_correct():
    """
    Ensures a data_type property is successfully validated and returns no errors
    when given an input that is part of the ACCEPTED_DATATYPE_MAPPING dictionary.
    """
    test_instance = TestClass(
        test_data_type="nonPositiveInteger",
    )
    errors = test_instance.validate()
    assert not any(errors)


def test_validate_data_type_looks_like_uri():
    """
    Ensures a data type property is successfully validated and returns no errors
    when given an input that is not part of the ACCEPTED_DATATYPE_MAPPING dictionary,
    but does look like a URI.
    """
    test_instance = TestClass(
        test_data_type="http://this/looks/like-a/uri",
    )
    errors = test_instance.validate()
    assert not any(errors)


def test_validate_data_type_incorrect():
    """
    Ensures a data type property is validated and correctly returns errors when given
    an input that is not part of the ACCEPTED_DATATYPE_MAPPING dictionary and does not
    look like a URI.
    """
    test_instance = TestClass(
        test_data_type="Definitely not a data type or URI",
    )
    errors = test_instance.validate()
    assert any(errors)


def test_validate_int_fails_when_bool():
    """
    Ensures validation of an integer correctly returns errors when a boolean is given as input.
    This is checking that we are not treating booleans as integers (the way python usually does) when validating.
    """
    test_instance = TestClass(int_test_variable=True)
    errors = test_instance.validate()
    assert any(errors)


@dataclass
class TestUnitClass(QbUnit):
    base_unit: Optional[QbUnit] = field(default=None, repr=False)
    base_unit_scaling_factor: Optional[float] = field(default=None, repr=False)
    qudt_quantity_kind_uri: Optional[str] = field(default=None, repr=False)
    si_base_unit_conversion_multiplier: Optional[float] = field(
        default=None, repr=False
    )

    def _get_validations(self) -> Union[Validations, Dict[str, ValidationFunction]]:
        return Validations(
            individual_property_validations={
                "base_unit": validate_optional(v.validated_model(QbUnit)),
                "base_unit_scaling_factor": validate_optional(validate_float_type),
                "qudt_quantity_kind_uri": validate_optional(validate_uri),
                "si_base_unit_conversion_multiplier": validate_optional(
                    validate_float_type
                ),
            },
            whole_object_validations=[
                NewQbUnit._validation_base_unit_scaling_factor_dependency
            ],
        )


def test_validate_base_unit_scaling_factor_dependency_correct():
    """
    Ensures whole-object validation can be performed on a NewQbUnit and account for the
    dependencies between base unit - base unit scaling factor, and also the dependency between
    qudt_quantity_kind_uri - si_base_unit_conversion_multiplier.
    (If one is none, then the other must be also.)
    """
    test_instance = TestUnitClass()
    errors = test_instance.validate()
    assert not any(errors)


def test_validate_base_unit_scaling_factor_dependency_incorrect():
    """
    Ensures whole-object validation can be performed on a NewQbUnit and account for the
    dependencies between base unit - base unit scaling factor (base unit must exist if
    scaling factor exists), and returning errors as expected.
    """
    test_instance = TestUnitClass(base_unit_scaling_factor=1.5)
    errors = test_instance.validate()
    assert any(errors)


def test_validate_base_unit_conversion_multiplier_dependency_incorrect():
    """
    Ensures whole-object validation can be performed on a NewQbUnit and account for the
    dependencies between qudt_quantity_kind_uri - si_base_unit_conversion_multiplier,
    and returning errors as expected.
    """
    test_instance = TestUnitClass(si_base_unit_conversion_multiplier=2.0)
    errors = test_instance.validate()
    assert any(errors)


def test_boolean_correct():
    """
    This test will validate if the class has been instanciated with a variable that was expecting a boolean,
    and was provided with the correct type variable.
    """
    test_instance = TestClass(bool_test_variable=False)

    result = test_instance.validate()

    assert len(result) == 0


def test_boolean_incorrect():
    """
    This test will validate if the class has been instanciated with a variable that was expecting an boolean,
    but it was provided with a non boolean type variable.
    """

    test_instance = TestClass(bool_test_variable=5)

    errors = test_instance.validate()

    assert any(errors)


if __name__ == "__main__":
    pytest.main()
