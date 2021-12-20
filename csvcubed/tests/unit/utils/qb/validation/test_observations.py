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
from csvcubed.utils.qb.validation.observations import get_observation_status_columns


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


if __name__ == "__main__":
    pytest.main()
