import pytest

from csvcubed.models.cube import NewQbUnit, ExistingQbUnit
from tests.unit.test_baseunit import assert_num_validation_errors


def test_new_unit_base_unit_validation():
    """
    Ensure that if either of :obj:`base_unit` or :obj:`base_unit_scaling_factor` are specified, and the other isn't,
    the user gets a suitable validation error.
    """
    _assert_both_properties_defined_error(
        NewQbUnit(
            "Some Unit",
            base_unit=ExistingQbUnit("http://existing-unit"),
            base_unit_scaling_factor=None,
        ),
        "base_unit",
        "base_unit_scaling_factor",
    )

    _assert_both_properties_defined_error(
        NewQbUnit(
            "Some Unit",
            base_unit=None,
            base_unit_scaling_factor=1000.0,
        ),
        "base_unit_scaling_factor",
        "base_unit",
    )

    # Now check that valid states don't trigger the error.
    assert_num_validation_errors(NewQbUnit("Some Unit").pydantic_validation(), 0)

    assert_num_validation_errors(
        NewQbUnit(
            "Some Unit",
            base_unit=ExistingQbUnit("http://some-existing-unit"),
            base_unit_scaling_factor=1000.0,
        ).pydantic_validation(),
        0,
    )


def _assert_both_properties_defined_error(
    unit: NewQbUnit, provided_variable_name: str, expected_variable_name: str
) -> None:
    errors = unit.pydantic_validation()
    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert provided_variable_name in str(error)
    assert expected_variable_name in str(error)


if __name__ == "__main__":
    pytest.main()
