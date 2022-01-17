from csvcubed.models.cube.qb.components.measure import ExistingQbMeasure
from csvcubed.models.cube.qb.components.measuresdimension import QbMultiMeasureDimension
from csvcubed.models.cube.qb.components.observedvalue import QbMultiMeasureObservationValue
import pytest


from csvcubed.models.cube import (
    ExistingQbAttribute,
    QbColumn,
    NewQbAttribute,
    NewQbUnit,
    NewQbMeasure,
    QbSingleMeasureObservationValue,
    NewQbDimension,
    CatalogMetadata,
    Cube,
)

from csvcubed.utils.qb.validation.observations import get_observation_status_columns, _validate_multi_measure_cube


def test_find_sdmxa_obs_status_columns():
    """
    Ensure that we can get `sdmxa:obsStatus` columns defined in various ways.
    """
    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=None,
        columns=[
            QbColumn("Some Dimension", NewQbDimension(label="Some Dimension")),
            QbColumn(
                "Values",
                QbSingleMeasureObservationValue(
                    NewQbMeasure("Some Measure"),
                    NewQbUnit("Some Unit"),
                ),
            ),
            QbColumn("Non SDMX Attribute", NewQbAttribute(label="Non SDMX Attribute")),
            QbColumn(
                "SDMX subPropertyOf Attribute",
                NewQbAttribute(
                    label="SDMX subPropertyOf Attribute",
                    parent_attribute_uri="http://purl.org/linked-data/sdmx/2009/attribute#obsStatus",
                ),
            ),
            QbColumn(
                "SDMX Obs Status Direct Attribute",
                ExistingQbAttribute(
                    "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus"
                ),
                csv_column_uri_template="https://example.org/some_attribute/{+Some_attribute}",
            ),
        ],
    )

    obs_status_columns = get_observation_status_columns(qube)
    assert len(obs_status_columns) == 2, obs_status_columns
    obs_status_col_names = {c.csv_column_title for c in obs_status_columns}
    assert obs_status_col_names == {
        "SDMX subPropertyOf Attribute",
        "SDMX Obs Status Direct Attribute",
    }, obs_status_col_names


def test_value_uri_template_is_present_in_existing_measure_dimention():
    """
    Testing to see that when the measure dimention is defined, that the value uri template is also defined.
    """
    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=None,
        columns=[
            QbColumn("Some Dimension", NewQbDimension(label="Some Dimension")),
            QbColumn(
                "Values",
                QbMultiMeasureObservationValue(
                    unit=NewQbUnit("Some Unit"),
                ),
            ),
            QbColumn(
                "Measure", 
                QbMultiMeasureDimension([
                    ExistingQbMeasure("http://some-measure")
                ]),
                csv_column_uri_template="http://some-uri/{+measure}"
            )
        ],
    )
    errors = _validate_multi_measure_cube(qube, None)
    assert len(errors) == 0, [e.message for e in errors]


def test_value_uri_template_is_missing_in_existing_measure_dimention():
    """
    Testing to see that the value uri template is not defined when the measure dimention is defined.
    """
    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=None,
        columns=[
            QbColumn("Some Dimension", NewQbDimension(label="Some Dimension")),
            QbColumn(
                "Values",
                QbMultiMeasureObservationValue(
                    unit=NewQbUnit("Some Unit"),
                ),
            ),
            QbColumn(
                "Measure", 
                QbMultiMeasureDimension([
                    ExistingQbMeasure("http://some-measure")
                ]),
            )
        ],
    )
    errors = _validate_multi_measure_cube(qube, None)
    assert len(errors) == 1, [e.message for e in errors]
    
if __name__ == "__main__":
    pytest.main()
