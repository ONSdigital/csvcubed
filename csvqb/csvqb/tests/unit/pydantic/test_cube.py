import pandas as pd
import pytest

from csvqb.models.cube import *
from csvqb.tests.unit.test_baseunit import assert_num_validation_errors


def test_attribute_property_validation():
    """Testing that the pydantic validation does deep validation of a model."""
    metadata = CatalogMetadata("Some Qube")
    data = pd.DataFrame({"A": ["a", "b", "c"], "Value": [1, 2, 3]})
    columns = [
        QbColumn(
            "A",
            NewQbDimension(
                "Some New Dimension",
                code_list=NewQbCodeList(
                    CatalogMetadata("Some Code List"),
                    # N.B. The Concepts shouldn't be strings, this should cause a validation error
                    concepts=["Hello", "World"],
                ),
            ),
        ),
        QbColumn(
            "Value",
            QbSingleMeasureObservationValue(
                NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
            ),
        ),
    ]

    cube = Cube(metadata, data, columns)
    errors = cube.validate()
    assert_num_validation_errors(errors, 2)

    # Ensure that the errors are related to the erroneous definition of the concepts as `str`s
    # rather than `NewQbConcept`s.
    error_1 = errors[0]
    assert (
        "('columns', 0, 'component', 'code_list', 'concepts', 0) - instance of NewQbConcept, tuple or dict expected"
        in error_1.message
    )
    error_2 = errors[1]
    assert (
        "('columns', 0, 'component', 'code_list', 'concepts', 1) - instance of NewQbConcept, tuple or dict expected"
        in error_2.message
    )


if __name__ == "__main__":
    pytest.main()
