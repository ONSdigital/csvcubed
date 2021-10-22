from csvqb.inputs import PandasDataTypes
from csvqb.models.cube.qb.components.attribute import NewQbAttributeValue
import pytest

import pandas as pd

from csvqb.models.cube import *
from csvqb.models.cube.qb.validationerrors import (
    CsvColumnUriTemplateMissingError,
    MinNumComponentsNotSatisfiedError,
    UnitsNotDefinedError,
    BothUnitTypesDefinedError,
    MaxNumComponentsExceededError,
    WrongNumberComponentsError,
    IncompatibleComponentsError,
)
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
            csv_column_uri_template="https://example.org/concept-scheme/existing_scheme/{+existing_dimension}",
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

    assert_num_validation_errors(validation_errors, 0)


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
            csv_column_uri_template="https://example.org/concept-scheme/existing_scheme/{+existing_dimension}",
        ),
        QbColumn("Value", QbMultiMeasureObservationValue(data_type="number")),
        QbColumn(
            "Measure",
            QbMultiMeasureDimension.new_measures_from_data(data["Measure"]),
        ),
        QbColumn("Units", QbMultiUnits.new_units_from_data(data["Units"])),
    ]

    cube = Cube(metadata, data, columns)
    validation_errors = cube.validate()
    validation_errors += validate_qb_component_constraints(cube)

    assert_num_validation_errors(validation_errors, 0)


def test_existing_dimension_csv_column_uri_template():
    """
    An ExistingQbDimension must have an csv_column_uri_template defined by the user if not it's an error
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
    validation_error = errors[0]
    assert isinstance(validation_error, CsvColumnUriTemplateMissingError)
    assert validation_error.csv_column_name == "Existing Dimension"


def test_no_dimensions_validation_error():
    """
    Ensure that we get an error message specifying that at least one dimension must be defined in a cube.
    """

    data = pd.DataFrame({"Value": [1, 2, 3]})
    cube = Cube(
        CatalogMetadata("Some Qube"),
        data,
        [
            QbColumn(
                "Value",
                QbSingleMeasureObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            )
        ],
    )

    errors = validate_qb_component_constraints(cube)

    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert isinstance(error, MinNumComponentsNotSatisfiedError)
    assert error.component_type == QbDimension
    assert error.minimum_number == 1
    assert error.actual_number == 0


def test_multiple_incompatible_unit_definitions():
    """
    Ensure that when we define a units column *and* an Observation value with a unit, that we get an error.
    """
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Some Unit": ["u1", "u2", "u1"],
            "Value": [1, 2, 3],
        }
    )

    cube = Cube(
        CatalogMetadata("Some Qube"),
        data,
        [
            QbColumn(
                "Some Dimension",
                NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
            ),
            QbColumn("Some Unit", QbMultiUnits.new_units_from_data(data["Some Unit"])),
            QbColumn(
                "Value",
                QbSingleMeasureObservationValue(
                    NewQbMeasure("Some New Measure"), NewQbUnit("Some New Unit")
                ),
            ),
        ],
    )
    errors = validate_qb_component_constraints(cube)

    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert isinstance(error, BothUnitTypesDefinedError)


def test_no_unit_defined():
    """
    Ensure that when we don't define a unit, we get an error message.
    """
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Value": [1, 2, 3],
        }
    )

    cube = Cube(
        CatalogMetadata("Some Qube"),
        data,
        [
            QbColumn(
                "Some Dimension",
                NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
            ),
            QbColumn(
                "Value",
                QbSingleMeasureObservationValue(NewQbMeasure("Some New Measure")),
            ),
        ],
    )
    errors = validate_qb_component_constraints(cube)

    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert isinstance(error, UnitsNotDefinedError)


def test_multiple_units_columns():
    """
    Ensure that when a user defines multiple units columns, we get an error.
    """
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Some Unit": ["u1", "u2", "u1"],
            "Some Other Unit": ["U1", "U2", "U3"],
            "Value": [1, 2, 3],
        }
    )

    cube = Cube(
        CatalogMetadata("Some Qube"),
        data,
        [
            QbColumn(
                "Some Dimension",
                NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
            ),
            QbColumn("Some Unit", QbMultiUnits.new_units_from_data(data["Some Unit"])),
            QbColumn(
                "Some Other Unit",
                QbMultiUnits.new_units_from_data(data["Some Other Unit"]),
            ),
            QbColumn(
                "Value",
                QbSingleMeasureObservationValue(NewQbMeasure("Some New Measure")),
            ),
        ],
    )
    errors = validate_qb_component_constraints(cube)

    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert isinstance(error, MaxNumComponentsExceededError)
    assert error.component_type == QbMultiUnits
    assert error.maximum_number == 1
    assert error.actual_number == 2


def test_multiple_obs_val_columns():
    """
    Ensure that when a user defines multiple observation value columns, we get an error.

    We only currently accept the `MeasureDimension` style of multi-measure datasets.
    """
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Value1": [3, 2, 1],
            "Value2": [1, 2, 3],
        }
    )

    cube = Cube(
        CatalogMetadata("Some Qube"),
        data,
        [
            QbColumn(
                "Some Dimension",
                NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
            ),
            QbColumn(
                "Value1",
                QbSingleMeasureObservationValue(
                    NewQbMeasure("Some New Measure 1"), NewQbUnit("Some New Unit 1")
                ),
            ),
            QbColumn(
                "Value2",
                QbSingleMeasureObservationValue(
                    NewQbMeasure("Some New Measure 2"), NewQbUnit("Some New Unit 2")
                ),
            ),
        ],
    )
    errors = validate_qb_component_constraints(cube)

    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert isinstance(error, WrongNumberComponentsError)
    assert error.component_type == QbObservationValue
    assert error.expected_number == 1
    assert error.actual_number == 2


def test_multi_measure_obs_val_without_measure_dimension():
    """
    Ensure that when a user defines a multi-measure observation valuer, we get a warning if they haven't defined a
    measure dimension.
    """
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Value": [1, 2, 3],
        }
    )

    cube = Cube(
        CatalogMetadata("Some Qube"),
        data,
        [
            QbColumn(
                "Some Dimension",
                NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
            ),
            QbColumn(
                "Value",
                QbMultiMeasureObservationValue(unit=NewQbUnit("Some New Unit 1")),
            ),
        ],
    )
    errors = validate_qb_component_constraints(cube)

    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert isinstance(error, WrongNumberComponentsError)
    assert error.component_type == QbMultiMeasureDimension
    assert error.expected_number == 1
    assert error.actual_number == 0
    assert (
        error.additional_explanation
        == "A multi-measure cube must have a measure dimension."
    )


def test_multi_measure_obs_val_with_multiple_measure_dimensions():
    """
    Ensure that a user gets an error if they try to define more than one measure dimension.
    """
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Measure Dimension 1": ["A1 Measure", "B1 Measure", "C1 Measure"],
            "Measure Dimension 2": ["A2 Measure", "B2 Measure", "C2 Measure"],
            "Value": [1, 2, 3],
        }
    )

    cube = Cube(
        CatalogMetadata("Some Qube"),
        data,
        [
            QbColumn(
                "Some Dimension",
                NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
            ),
            QbColumn(
                "Measure Dimension 1",
                QbMultiMeasureDimension.new_measures_from_data(
                    data["Measure Dimension 1"]
                ),
            ),
            QbColumn(
                "Measure Dimension 2",
                QbMultiMeasureDimension.new_measures_from_data(
                    data["Measure Dimension 2"]
                ),
            ),
            QbColumn(
                "Value",
                QbMultiMeasureObservationValue(unit=NewQbUnit("Some New Unit 1")),
            ),
        ],
    )
    errors = validate_qb_component_constraints(cube)

    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert isinstance(error, MaxNumComponentsExceededError)
    assert error.component_type == QbMultiMeasureDimension
    assert error.maximum_number == 1
    assert error.actual_number == 2


def test_measure_dimension_with_single_measure_obs_val():
    """
    Ensure that when a user defines a measure dimension with a single-measure observation value, they get an error.
    """
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Measure Dimension": ["A Measure", "B Measure", "C Measure"],
            "Value": [1, 2, 3],
        }
    )

    cube = Cube(
        CatalogMetadata("Some Qube"),
        data,
        [
            QbColumn(
                "Some Dimension",
                NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
            ),
            QbColumn(
                "Measure Dimension",
                QbMultiMeasureDimension.new_measures_from_data(
                    data["Measure Dimension"]
                ),
            ),
            QbColumn(
                "Value",
                QbSingleMeasureObservationValue(
                    NewQbMeasure("Some New Measure"), NewQbUnit("Some New Unit 1")
                ),
            ),
        ],
    )
    errors = validate_qb_component_constraints(cube)

    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert isinstance(error, IncompatibleComponentsError)
    assert error.component_one == QbSingleMeasureObservationValue
    assert error.component_two == QbMultiMeasureDimension
    assert (
        error.additional_explanation
        == "A single-measure cube cannot have a measure dimension."
    )


def test_existing_attribute_csv_column_uri_template_required():
    """
    An ExistingQbAttribute using Existing Attribute Values must have an csv_column_uri_template defined by the user,
     if not it's an error
    """

    data = pd.DataFrame(
        {
            "Existing Dimension": ["A", "B", "C"],
            "Existing Attribute 1": ["Val1", "Val2", "Val3"],
            "Existing Attribute 2": ["Val4", "Val5", "Val6"],
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
                csv_column_uri_template="https://example.org/concept-scheme/existing_scheme/{+existing_dimension}",
            ),
            QbColumn(
                "Existing Attribute 1",
                ExistingQbAttribute("http://example.org/attributes/example"),
                # No NewQbAttributeValues - so csv_column_uri_template is *required*
            ),
            QbColumn(
                "Existing Attribute 2",
                ExistingQbAttribute(
                    "http://example.org/attributes/example",
                    new_attribute_values=[
                        NewQbAttributeValue("Val4"),
                        NewQbAttributeValue("Val5"),
                        NewQbAttributeValue("Val6"),
                    ],
                ),
                # NewQbAttributeValues defined - so csv_column_uri_template is **not** required
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

    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert isinstance(error, CsvColumnUriTemplateMissingError)
    assert error.csv_column_name == "Existing Attribute 1"
    assert error.component_type == "ExistingQbAttribute using existing attribute values"


def test_new_attribute_csv_column_uri_template_required():
    """
    A NewQbAttribute using existing attribute vluaes must have an csv_column_uri_template defined by the user,
     if not it's an error
    """

    data = pd.DataFrame(
        {
            "Existing Dimension": ["A", "B", "C"],
            "New Attribute 1": ["Val1", "Val2", "Val3"],
            "New Attribute 2": ["Val4", "Val5", "Val6"],
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
                csv_column_uri_template="https://example.org/concept-scheme/existing_scheme/{+existing_dimension}",
            ),
            QbColumn(
                "New Attribute 1",
                NewQbAttribute("Some New Attribute 1"),
                # No NewQbAttributeValues - so csv_column_uri_template is *required*
            ),
            QbColumn(
                "New Attribute 2",
                NewQbAttribute(
                    "Some New Attribute 2",
                    new_attribute_values=[
                        NewQbAttributeValue("Val4"),
                        NewQbAttributeValue("Val5"),
                        NewQbAttributeValue("Val6"),
                    ],
                ),
                # NewQbAttributeValues defined - so csv_column_uri_template is **not** required
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

    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert isinstance(error, CsvColumnUriTemplateMissingError)
    assert error.csv_column_name == "New Attribute 1"
    assert error.component_type == "NewQbAttribute using existing attribute values"


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


# Literal tests go here
def _create_simple_frame_with_literals(data_type: str):
    df = pd.DataFrame({
        "Some Dimension": ["a", "b", "c"],
        "Values": [1, 2, 3]
    })
    if data_type in ("string", "str"):
        df["Some Attribute"] = ["one", "two", "three"]
    elif data_type in ("int"):
        df["Some Attribute"] = [11, 12, 13]
    elif data_type in ("date"):
        df["Some Attribute"] = ["2020-10-01", "2010-10-10", "2112-12-21"]
    
    return df

def test_qb_attribute_literal_new_string():
    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=_create_simple_frame_with_literals("str"),
        columns=[
            QbColumn(
                "Some Dimension",
                NewQbDimension(label="Some Dimension")
            ),
            QbColumn(
                "Values",
                QbSingleMeasureObservationValue(
                    NewQbMeasure("Some Measure"),
                    NewQbUnit("Some Unit"),                   
                )
            ),
            QbColumn(
                "Some Attribute",
                NewQbAttributeLiteral(
                    data_type="string",
                    label="Some Attribute"
                )
            )
        ]
    )

    errors = qube.validate()

    assert len(errors) == 0

if __name__ == "__main__":
    pytest.main()
