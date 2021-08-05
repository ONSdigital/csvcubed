from csvqb.inputs import PandasDataTypes
from csvqb.models.cube.csvqb.components.attribute import NewQbAttributeValue
import pytest

import pandas as pd

from csvqb.models.cube import *
from csvqb.tests.unit.test_baseunit import *
from csvqb.utils.qb.cube import validate_qb_component_constraints


def test_single_measure_qb_definition():
    """
    Single-measure Qbs can be defined.
    """
    data = pd.DataFrame(
        {
            "Existing Dimension": ["A", "B", "C"],
            "Local Dimension": ["D", "E", "F"],
            "Value": [2, 2, 2],
        }
    )

    metadata = CatalogMetadata("Some Dataset")
    columns = [
        QbColumn(
            "Existing Dimension",
            ExistingQbDimension("https://example.org/dimensions/existing_dimension"),
            output_uri_template="https://example.org/concept-scheme/existing_scheme/{+existing_dimension}",
        ),
        QbColumn(
            "Local Dimension",
            NewQbDimension.from_data("Dimension of letters", data["Local Dimension"]),
        ),
        QbColumn(
            "Value",
            QbSingleMeasureObservationValue(
                ExistingQbMeasure("http://example.com/measures/existing_measure"),
                NewQbUnit("some new unit"),
            ),
        ),
    ]

    cube = Cube(metadata, data, columns)
    validation_errors = cube.validate()
    validation_errors += validate_qb_component_constraints(cube)

    assert len(validation_errors) == 0


def test_multi_measure_qb_definition():
    """
    Multi-measure Qbs can be defined.
    """
    data = pd.DataFrame(
        {
            "Existing Dimension": ["A", "B", "C"],
            "Value": [2, 2, 2],
            "Measure": ["People", "Children", "Adults"],
            "Units": ["Percent", "People", "People"],
        }
    )

    metadata = CatalogMetadata("Some Dataset")
    columns = [
        QbColumn(
            "Existing Dimension",
            ExistingQbDimension("https://example.org/dimensions/existing_dimension"),
            output_uri_template="https://example.org/concept-scheme/existing_scheme/{+existing_dimension}",
        ),
        QbColumn("Value", QbMultiMeasureObservationValue(data_type="number")),
        QbColumn(
            "Measure", QbMultiMeasureDimension.new_measures_from_data(data["Measure"]),
        ),
        QbColumn("Units", QbMultiUnits.new_units_from_data(data["Units"])),
    ]

    cube = Cube(metadata, data, columns)
    validation_errors = cube.validate()
    validation_errors += validate_qb_component_constraints(cube)

    assert len(validation_errors) == 0


def test_existing_dimension_output_uri_template():
    """
    An ExistingQbDimension must have an output_uri_template defined by the user if not it's an error

    """

    data = pd.DataFrame({"Existing Dimension": ["A", "B", "C"], "Value": [1, 2, 3]})
    cube = Cube(
        CatalogMetadata("Cube's name"),
        data,
        [
            QbColumn(
                "Existing Dimension",
                ExistingQbDimension("http://example.org/dimensions/location"),
            ),
            QbColumn(
                "Value",
                QbSingleMeasureObservationValue(
                    ExistingQbMeasure("http://some/measure"),
                    ExistingQbUnit("http://some/unit"),
                ),
            ),
        ],
    )

    errors = cube.validate()
    errors += validate_qb_component_constraints(cube)

    assert_num_validation_errors(errors, 1)
    validation_errors = errors[0]
    assert (
        "'Existing Dimension' - an ExistingQbDimension must have an output_uri_template defined."
        in validation_errors.message
    )


def test_existing_attribute_output_uri_template():
    """
    An ExistingQbAttribute must have an output_uri_template defined by the user if not it's an error

    """

    data = pd.DataFrame(
        {
            "Existing Dimension": ["A", "B", "C"],
            "Existing Attribute": [1, 2, 3],
            "Obs": [6, 7, 8],
        }
    )
    cube = Cube(
        CatalogMetadata("Cube's name"),
        data,
        [
            QbColumn(
                "Existing Dimension",
                ExistingQbDimension("http://example.org/dimensions/location"),
                output_uri_template="https://example.org/concept-scheme/existing_scheme/{+existing_dimension}",
            ),
            QbColumn(
                "Existing Attribute",
                ExistingQbAttribute("http://example.org/attributes/example"),
            ),
            QbColumn(
                "Obs",
                QbSingleMeasureObservationValue(
                    ExistingQbMeasure("http://example.org/single/measure/example"),
                    NewQbUnit("GBP"),
                ),
            ),
        ],
    )

    errors = cube.validate()
    errors += validate_qb_component_constraints(cube)

    assert len(errors) == 1
    validation_errors = errors[0]
    assert (
        "'Existing Attribute' - an ExistingQbAttribute must have an output_uri_template defined."
        in validation_errors.message
    )


def test_new_qb_attribute_generation():
    """
    When a new attribute value is defined from the dataframe, ensure that only unique attribute values are generated.
    """

    data = pd.DataFrame(
        {
            "Year": [2020, 2019, 2018],
            "Value": [5.6, 2.8, 4.4],
            "Marker": ["Provisional", "Final", "Final"],
        }
    )

    marker_attribute = NewQbAttribute.from_data(label="Status", data=data["Marker"])

    assert len(marker_attribute.new_attribute_values) == 2

    new_value_set = {
        new_attribute_value.label
        for new_attribute_value in marker_attribute.new_attribute_values
    }

    assert new_value_set == {"Provisional", "Final"}


if __name__ == "__main__":
    pytest.main()
