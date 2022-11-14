import pytest

from csvcubed.models.cube import *
from csvcubed.models.cube.cube import Cube
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.cube.qb.components.measure import NewQbMeasure
from csvcubed.models.cube.qb.components.measuresdimension import QbMultiMeasureDimension
from csvcubed.models.cube.qb.components.observedvalue import QbObservationValue
from csvcubed.models.cube.qb.components.unit import NewQbUnit
from csvcubed.models.cube.qb.components.unitscolumn import QbMultiUnits
from csvcubed.utils.qb.cube import get_all_units, get_all_measures


def test_get_all_units():
    cube = Cube(
        CatalogMetadata("Some Qube"),
        None,
        [
            QbColumn(
                "Some Multi Units Column",
                QbMultiUnits(
                    [NewQbUnit("Unit 1"), NewQbUnit("Unit 2"), NewQbUnit("Unit 1")]
                ),
            ),
            QbColumn(
                "Some Multi Measure Obs Val",
                QbObservationValue(unit=NewQbUnit("Unit 3")),
            ),
            QbColumn(
                "Some Single Measure Obs Val",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), unit=NewQbUnit("Unit 4")
                ),
            ),
        ],
    )

    units = get_all_units(cube)

    assert units == {
        NewQbUnit("Unit 1"),
        NewQbUnit("Unit 2"),
        NewQbUnit("Unit 3"),
        NewQbUnit("Unit 4"),
    }


def test_get_all_measures():
    cube = Cube(
        CatalogMetadata("Some Qube"),
        None,
        [
            QbColumn(
                "Some Multi Measure Column",
                QbMultiMeasureDimension(
                    [
                        NewQbMeasure("Measure 1"),
                        NewQbMeasure("Measure 2"),
                        NewQbMeasure("Measure 1"),
                    ]
                ),
            ),
            QbColumn(
                "Some Single Measure Obs Val",
                QbObservationValue(NewQbMeasure("Measure 3")),
            ),
        ],
    )

    measures = get_all_measures(cube)

    assert measures == {
        NewQbMeasure("Measure 1"),
        NewQbMeasure("Measure 2"),
        NewQbMeasure("Measure 3"),
    }


if __name__ == "__main__":
    pytest.main()
