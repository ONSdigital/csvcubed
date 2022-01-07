import pandas as pd
import pytest

from csvcubed.models.cube import (
    NewQbUnit,
    QbColumn,
    ExistingQbUnit,
    QbMultiUnits,
)
from csvcubed.models.cube.qb.components.validationerrors import UndefinedUnitUrisError
from tests.unit.test_baseunit import assert_num_validation_errors


def test_known_new_units_defined():
    """Ensure that we don't get any errors raised when newly defined units are used."""
    data = pd.DataFrame({"Unit": ["unit-1", "unit-2"]})
    unit_column = QbColumn(
        "Unit",
        QbMultiUnits([NewQbUnit("Unit 1"), NewQbUnit("Unit 2")]),
    )

    unit_dimension = unit_column.structural_definition

    errors = unit_dimension.validate_data(data["Unit"], "unit", "{+unit}")
    assert_num_validation_errors(errors, 0)


def test_unknown_new_units_error():
    """Ensure that we get an error when units are used which we're not aware of."""
    data = pd.DataFrame({"Unit": ["unit-1", "unit-3"]})
    unit_column = QbColumn(
        "Unit",
        QbMultiUnits([NewQbUnit("Unit 1"), NewQbUnit("Unit 2")]),
    )

    unit_dimension = unit_column.structural_definition

    errors = unit_dimension.validate_data(data["Unit"], "unit", "{+unit}")
    assert_num_validation_errors(errors, 1)

    error = errors[0]
    assert isinstance(error, UndefinedUnitUrisError)
    assert isinstance(error.component, QbMultiUnits)
    assert error.undefined_values == {"unit-3"}


def test_known_existing_units_defined():
    """Ensure that we don't get any errors raised when existing units are used."""
    data = pd.DataFrame({"Unit": ["unit-1", "unit-2"]})
    unit_column = QbColumn(
        "Unit",
        QbMultiUnits(
            [
                ExistingQbUnit("http://example.org/units/unit-1"),
                ExistingQbUnit("http://example.org/units/unit-2"),
            ]
        ),
    )

    unit_dimension = unit_column.structural_definition

    errors = unit_dimension.validate_data(
        data["Unit"], "unit", "http://example.org/units/{+unit}"
    )
    assert_num_validation_errors(errors, 0)


def test_unknown_existing_units_error():
    """Ensure that we get an error when existing units are used which we're not aware of."""
    data = pd.DataFrame({"Unit": ["unit-1", "unit-3"]})
    unit_column = QbColumn(
        "Unit",
        QbMultiUnits(
            [
                ExistingQbUnit("http://example.org/units/unit-1"),
                ExistingQbUnit("http://example.org/units/unit-2"),
            ]
        ),
    )

    multi_units_component = unit_column.structural_definition

    errors = multi_units_component.validate_data(
        data["Unit"], "unit", "http://example.org/units/{+unit}"
    )
    assert_num_validation_errors(errors, 1)

    error = errors[0]
    assert isinstance(error, UndefinedUnitUrisError)
    assert isinstance(error.component, QbMultiUnits)
    assert error.undefined_values == {"http://example.org/units/unit-3"}


if __name__ == "__main__":
    pytest.main()
