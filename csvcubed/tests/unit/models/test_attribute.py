import pandas as pd
import pytest

from csvcubed.models.cube import (
    QbMultiMeasureDimension,
    NewQbMeasure,
    QbColumn,
    ExistingQbMeasure,
)
from csvcubed.models.cube.qb.components.validationerrors import (
    UndefinedMeasureUrisError,
)
from tests.unit.test_baseunit import assert_num_validation_errors


def test_known_new_measures_defined():
    """Ensure that we don't get any errors raised when newly defined measures are used."""
    data = pd.DataFrame({"Measure": ["measure-1", "measure-2"]})
    measure_column = QbColumn(
        "Measure",
        QbMultiMeasureDimension([NewQbMeasure("Measure 1"), NewQbMeasure("Measure 2")]),
    )

    measure_dimension = measure_column.component

    errors = measure_dimension.validate_data(data["Measure"], "measure", "{+measure}")
    assert_num_validation_errors(errors, 0)


def test_known_existing_measures_defined():
    """Ensure that we don't get any errors raised when existing measures are used."""
    data = pd.DataFrame({"Measure": ["measure-1", "measure-2"]})
    measure_column = QbColumn(
        "Measure",
        QbMultiMeasureDimension(
            [
                ExistingQbMeasure("http://example.org/measures/measure-1"),
                ExistingQbMeasure("http://example.org/measures/measure-2"),
            ]
        ),
    )

    measure_dimension = measure_column.component

    errors = measure_dimension.validate_data(
        data["Measure"], "measure", "http://example.org/measures/{+measure}"
    )
    assert_num_validation_errors(errors, 0)


def test_known_new_measures_undefined():
    """Ensure that when a user uses a new measure which hasn't been defined, they get an error."""
    data = pd.DataFrame({"Measure": ["measure-1", "measure-2"]})
    measure_column = QbColumn(
        "Measure",
        QbMultiMeasureDimension([NewQbMeasure("Measure 1"), NewQbMeasure("Measure 3")]),
    )

    measure_dimension = measure_column.component

    errors = measure_dimension.validate_data(data["Measure"], "measure", "{+measure}")
    assert_num_validation_errors(errors, 1)
    error = errors[0]

    assert isinstance(error, UndefinedMeasureUrisError)
    assert isinstance(error.component, QbMultiMeasureDimension)
    assert error.undefined_values == {"measure-2"}


def test_known_existing_measures_undefined():
    """Ensure that when a user uses an existing measure which hasn't been defined, they get an error."""
    data = pd.DataFrame({"Measure": ["measure-1", "measure-2"]})
    measure_column = QbColumn(
        "Measure",
        QbMultiMeasureDimension(
            [
                ExistingQbMeasure("http://example.org/measures/measure-1"),
                ExistingQbMeasure("http://example.org/measures/measure-3"),
            ]
        ),
    )

    measure_dimension = measure_column.component

    errors = measure_dimension.validate_data(
        data["Measure"], "measure", "http://example.org/measures/{+measure}"
    )
    assert_num_validation_errors(errors, 1)
    error = errors[0]

    assert isinstance(error, UndefinedMeasureUrisError)
    assert isinstance(error.component, QbMultiMeasureDimension)
    assert error.undefined_values == {"http://example.org/measures/measure-2"}


if __name__ == "__main__":
    pytest.main()
