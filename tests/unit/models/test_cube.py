import pytest

from csvcubed.models.cube.cube import Cube
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.cube.qb.components.attribute import NewQbAttribute
from csvcubed.models.cube.qb.components.dimension import ExistingQbDimension
from csvcubed.models.cube.qb.components.measure import NewQbMeasure
from csvcubed.models.cube.qb.components.measuresdimension import QbMultiMeasureDimension
from csvcubed.models.cube.qb.components.observedvalue import QbObservationValue
from csvcubed.models.cube.qb.components.unit import NewQbUnit


def test_is_cube_in_pivoted_shape_true_for_pivoted_shape_cube():
    """
    Ensure that the boolean returned for an input cube of pivoted shape is true.
    """
    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn(
                "Some Dimension",
                ExistingQbDimension(
                    "https://example.org/dimensions/existing_dimension"
                ),
            ),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            QbColumn(
                "Some Obs Val",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
            QbColumn(
                "Some Other Obs Val",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
    )

    assert cube.is_pivoted_shape


def test_is_cube_in_pivoted_shape_false_for_standard_shape_cube():
    """
    Ensure that the boolean returned for an input cube of pivoted shape is false.
    """
    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn(
                "Some Dimension",
                ExistingQbDimension(
                    "https://example.org/dimensions/existing_dimension"
                ),
            ),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            QbColumn("Some Obs Val", QbObservationValue(unit=NewQbUnit("Some Unit"))),
            QbColumn(
                "Some Measure", QbMultiMeasureDimension([NewQbMeasure("New Measure")])
            ),
        ],
    )

    assert not cube.is_pivoted_shape


def test_is_cube_in_pivoted_shape_raise_exception():
    """
    Ensures that an exception is raised when the cube is in both the pivoted and standard shape.
    """
    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn(
                "Some Dimension",
                ExistingQbDimension(
                    "https://example.org/dimensions/existing_dimension"
                ),
            ),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            QbColumn("Some Obs Val", QbObservationValue(unit=NewQbUnit("Some Unit"))),
            QbColumn(
                "Some Other Obs Val",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
    )

    with pytest.raises(Exception) as err:
        cube.is_pivoted_shape

    assert str(err.value) == "The cube cannot be in both standard and pivoted shape"


if __name__ == "__main__":
    pytest.main()
