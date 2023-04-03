import pandas as pd
import pytest

from csvcubed.models.cube.cube import Cube
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.cube.qb.components.attribute import ExistingQbAttribute
from csvcubed.models.cube.qb.components.codelist import NewQbCodeList
from csvcubed.models.cube.qb.components.dimension import NewQbDimension
from csvcubed.models.cube.qb.components.measure import NewQbMeasure
from csvcubed.models.cube.qb.components.observedvalue import QbObservationValue
from csvcubed.models.cube.qb.components.unit import NewQbUnit
from csvcubed.models.validationerror import PydanticValidationError
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
            QbObservationValue(NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")),
        ),
    ]

    cube = Cube(metadata, data, columns)
    errors = cube.validate()
    assert_num_validation_errors(errors, 2)

    # Ensure that the errors are related to the erroneous definition of the concepts as `str`s
    # rather than `NewQbConcept`s.
    error_1 = errors[0]
    assert isinstance(error_1, PydanticValidationError)
    assert error_1.path == [
        "('columns', 0)",
        "structural_definition",
        "code_list",
        "('concepts', 0)",
    ]
    assert (
        str(error_1.original_error)
        == "instance of NewQbConcept, tuple or dict expected"
    )
    assert (
        error_1.message
        == "('columns', 0), structural_definition, code_list, ('concepts', 0) - instance of NewQbConcept, "
        "tuple or dict expected"
    )

    error_2 = errors[1]
    assert isinstance(error_2, PydanticValidationError)

    assert error_2.path == [
        "('columns', 0)",
        "structural_definition",
        "code_list",
        "('concepts', 1)",
    ]
    assert (
        str(error_2.original_error)
        == "instance of NewQbConcept, tuple or dict expected"
    )
    assert (
        error_2.message
        == "('columns', 0), structural_definition, code_list, ('concepts', 1) - instance of NewQbConcept, "
        "tuple or dict expected"
    )


if __name__ == "__main__":
    pytest.main()
