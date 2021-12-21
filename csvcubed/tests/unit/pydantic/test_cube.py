import pandas as pd
import pytest

from csvcubed.models.cube import *
from csvcubed.models.cube import ExistingQbAttribute
from tests.unit.test_baseunit import assert_num_validation_errors


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
        "('columns', 0, 'structural_definition', 'code_list', 'concepts', 0) - instance of NewQbConcept, tuple or dict expected"
        in error_1.message
    )
    error_2 = errors[1]
    assert (
        "('columns', 0, 'structural_definition', 'code_list', 'concepts', 1) - instance of NewQbConcept, tuple or dict expected"
        in error_2.message
    )


def test_deep_custom_validator():
    """Testing that the pydantic custom validation functions work, even when doing deep validation."""
    metadata = CatalogMetadata("Some Qube")
    data = pd.DataFrame(
        {
            "New Dimension": ["a", "b", "c"],
            "Existing Attribute": ["d", "e", "f"],
            "Value": [1, 2, 3],
        }
    )
    columns = [
        QbColumn(
            "New Dimension",
            NewQbDimension.from_data("Some New Dimension", data["New Dimension"]),
        ),
        QbColumn(
            "Existing Attribute", ExistingQbAttribute("this-should-not-look-like-a-uri")
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
    assert_num_validation_errors(errors, 1)

    error = errors[0]
    assert "does not look like a URI" in error.message


if __name__ == "__main__":
    pytest.main()
