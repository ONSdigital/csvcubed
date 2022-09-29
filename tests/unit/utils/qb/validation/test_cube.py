import pytest

from csvcubed.models.cube import (
    CsvColumnLiteralWithUriTemplate,
    NewQbAttributeLiteral,
    QbColumn,
    NewQbUnit,
    NewQbMeasure,
    QbObservationValue,
    NewQbDimension,
    CatalogMetadata,
    Cube,
)
from csvcubed.utils.qb.validation.cube import validate_qb_component_constraints


def test_new_qb_attribute_literal_string_with_template():
    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=None,
        columns=[
            QbColumn("Some Dimension", NewQbDimension(label="Some Dimension")),
            QbColumn(
                "Values",
                QbObservationValue(
                    NewQbMeasure("Some Measure"),
                    NewQbUnit("Some Unit"),
                ),
            ),
            QbColumn(
                "Some Attribute",
                NewQbAttributeLiteral(data_type="date", label="Some Attribute"),
                csv_column_uri_template="https://example.org/some_attribute/{+some_attribute}",
            ),
        ],
    )

    assert len(qube.validate()) == 0
    assert isinstance(
        validate_qb_component_constraints(qube)[0], CsvColumnLiteralWithUriTemplate
    )


if __name__ == "__main__":
    pytest.main()
