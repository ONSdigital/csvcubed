import pytest
import os

import pandas as pd

from csvcubed.models.cube import *
from csvcubed.models.cube import NewQbAttribute, QbMultiMeasureDimension, QbMultiUnits
from csvcubed.models.cube.qb.components.validationerrors import (
    ConflictingUriSafeValuesError,
    ReservedUriValueError,
)
from csvcubed.models.cube.qb.validationerrors import (
    CsvColumnUriTemplateMissingError,
    MinNumComponentsNotSatisfiedError,
    NoUnitsDefinedError,
    BothUnitTypesDefinedError,
    MaxNumComponentsExceededError,
)
from tests.unit.test_baseunit import *
from csvcubed.utils.qb.validation.cube import validate_qb_component_constraints
from csvcubed.utils.qb.validation.observations import _validate_pivoted_shape_cube


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
            QbObservationValue(
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
        QbColumn("Value", QbObservationValue(data_type="number")),
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
                QbObservationValue(
                    ExistingQbMeasure("http://some/measure"),
                    ExistingQbUnit("http://some/unit"),
                ),
            ),
        ],
    )

    validation_error = _get_single_validation_error_for_qube(cube)
    assert isinstance(validation_error, CsvColumnUriTemplateMissingError)
    assert validation_error.csv_column_name == "Existing Dimension"

    assert isinstance(validation_error.get_error_url(), str)
    assert (
        validation_error.get_error_url()
        == "http://purl.org/csv-cubed/err/csv-col-uri-temp-mis"
    )


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
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            )
        ],
    )

    error = _get_single_validation_error_for_qube(cube)
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
                QbObservationValue(
                    NewQbMeasure("Some New Measure"), NewQbUnit("Some New Unit")
                ),
            ),
        ],
    )

    validation_error = _get_single_validation_error_for_qube(cube)
    assert isinstance(validation_error, BothUnitTypesDefinedError)

    assert isinstance(validation_error.get_error_url(), str)
    assert (
        validation_error.get_error_url()
        == "http://purl.org/csv-cubed/err/both-unit-typ-def"
    )


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
                QbObservationValue(NewQbMeasure("Some New Measure")),
            ),
        ],
    )
    validation_error = _get_single_validation_error_for_qube(cube)
    assert isinstance(validation_error, NoUnitsDefinedError)

    assert isinstance(validation_error.get_error_url(), str)
    assert validation_error.get_error_url() == "http://purl.org/csv-cubed/err/no-unit"


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
                QbObservationValue(NewQbMeasure("Some New Measure")),
            ),
        ],
    )
    error = _get_single_validation_error_for_qube(cube)
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
                QbObservationValue(
                    NewQbMeasure("Some New Measure 1"), NewQbUnit("Some New Unit 1")
                ),
            ),
            QbColumn(
                "Value2",
                QbObservationValue(
                    NewQbMeasure("Some New Measure 2"), NewQbUnit("Some New Unit 2")
                ),
            ),
        ],
    )
    error = _get_single_validation_error_for_qube(cube)
    assert isinstance(error, MoreThanOneObservationsColumnError)
    assert error.component_type == QbObservationValue
    assert error.maximum_number == 1
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
                QbObservationValue(unit=NewQbUnit("Some New Unit 1")),
            ),
        ],
    )
    error = _get_single_validation_error_for_qube(cube)
    assert isinstance(error, NoMeasuresDefinedError)

    assert isinstance(error.get_error_url(), str)
    assert error.get_error_url() == "http://purl.org/csv-cubed/err/no-meas"


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
                QbObservationValue(unit=NewQbUnit("Some New Unit 1")),
            ),
        ],
    )
    error = _get_single_validation_error_for_qube(cube)
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
                QbObservationValue(
                    NewQbMeasure("Some New Measure"), NewQbUnit("Some New Unit 1")
                ),
            ),
        ],
    )
    error = _get_single_validation_error_for_qube(cube)
    assert isinstance(error, BothMeasureTypesDefinedError)
    assert error.component_one == f"{QbObservationValue.__name__}.measure"
    assert error.component_two == QbMultiMeasureDimension
    assert (
        error.additional_explanation
        == "A pivoted shape cube cannot have a measure dimension."
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
                QbObservationValue(
                    ExistingQbMeasure("http://example.org/single/measure/example"),
                    NewQbUnit("GBP"),
                ),
            ),
        ],
    )

    error = _get_single_validation_error_for_qube(cube)
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
                QbObservationValue(
                    ExistingQbMeasure("http://example.org/single/measure/example"),
                    NewQbUnit("GBP"),
                ),
            ),
        ],
    )

    error = _get_single_validation_error_for_qube(cube)
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
    df = pd.DataFrame({"Some Dimension": ["a", "b", "c"], "Values": [1, 2, 3]})
    if data_type in ("string", "str"):
        df["Some Attribute"] = ["one", "two", "three"]
    elif data_type in ("int"):
        df["Some Attribute"] = [11, 12, 13]
    elif data_type in ("date"):
        df["Some Attribute"] = ["2020-10-01", "2010-10-10", "2112-12-21"]
    elif data_type == "float":
        df["Some Attribute"] = [1.0, 2.0, 3.0]

    return df


def test_new_qb_attribute_literal_int():
    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=_create_simple_frame_with_literals("int"),
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
                NewQbAttributeLiteral(data_type="int", label="Some Attribute"),
            ),
        ],
    )

    assert_num_validation_errors(qube.validate(), 0)


def test_existing_qb_attribute_literal_date():
    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=_create_simple_frame_with_literals("date"),
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
                ExistingQbAttributeLiteral(
                    data_type="date", attribute_uri="https://example.org/attribute/date"
                ),
            ),
        ],
    )

    assert_num_validation_errors(qube.validate(), 0)


def test_attribute_numeric_resources_validation():
    """
    Ensuring that we can define a :class:`~csvcubed.models.cube.qb.components.attribute.NewQbAttribute` column
    holding :class:`~csvcubed.models.cube.qb.components.attribute.NewQbAttributeValue` instances defined by
    numeric (float) values.
    """
    data = _create_simple_frame_with_literals("float")
    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=data,
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
                NewQbAttribute.from_data(
                    label="Some Attribute", data=data["Some Attribute"]
                ),
            ),
        ],
    )
    errors = qube.validate()
    assert_num_validation_errors(errors, 0)


def test_code_list_concept_identifier_reserved():
    """
    Test that if the user tries to define a code-list with a concept which would use the reserved `code-list`
    identifier then they get a suitable validation error.
    """
    data = pd.DataFrame(
        {
            "New Dimension": ["A", "B", "C", "Code List"],
            "Value": [2, 2, 2, 2],
        }
    )

    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=data,
        columns=[
            QbColumn(
                "New Dimension",
                NewQbDimension.from_data("New Dimension", data["New Dimension"]),
            ),
            QbColumn(
                "Value",
                QbObservationValue(
                    NewQbMeasure("Some Measure"),
                    NewQbUnit("Some Unit"),
                ),
            ),
        ],
    )
    error = _get_single_validation_error_for_qube(qube)
    assert isinstance(error, ReservedUriValueError)
    assert error.component == NewQbCodeList
    assert error.reserved_identifier == "code-list"
    assert error.conflicting_values == ["Code List"]


def test_conflict_concept_uri_values_error():
    """
    Test that a validation error is raised when the user defines labels which are distinct, but map to the same
    URI-safe value.
    """
    data = pd.DataFrame(
        {
            "New Dimension": ["A B", "A.B"],
            "Value": [2, 2],
        }
    )

    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=data,
        columns=[
            QbColumn(
                "New Dimension",
                NewQbDimension.from_data("New Dimension", data["New Dimension"]),
            ),
            QbColumn(
                "Value",
                QbObservationValue(
                    NewQbMeasure("Some Measure"),
                    NewQbUnit("Some Unit"),
                ),
            ),
        ],
    )
    error = _get_single_validation_error_for_qube(qube)
    assert isinstance(error, ConflictingUriSafeValuesError)
    assert error.component_type == NewQbCodeList
    assert error.path == [
        "('columns', 0)",
        "structural_definition",
        "code_list",
        "concepts",
    ]
    assert error.map_uri_safe_values_to_conflicting_labels == {"a-b": {"A B", "A.B"}}


def test_conflict_new_attribute_value_uri_values_error():
    """
    Test that a validation error is raised when the user defines new attribute value labels (on a new attribute)
     which are distinct but map to the same URI-safe value.
    """
    data = pd.DataFrame(
        {
            "New Dimension": ["A", "B"],
            "New Attribute": ["A B", "A.B"],
            "Value": [2, 2],
        }
    )

    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=data,
        columns=[
            QbColumn(
                "New Dimension",
                NewQbDimension.from_data("New Dimension", data["New Dimension"]),
            ),
            QbColumn(
                "New Attribute",
                NewQbAttribute.from_data("New Attribute", data["New Attribute"]),
            ),
            QbColumn(
                "Value",
                QbObservationValue(
                    NewQbMeasure("Some Measure"),
                    NewQbUnit("Some Unit"),
                ),
            ),
        ],
    )
    error = _get_single_validation_error_for_qube(qube)
    assert isinstance(error, ConflictingUriSafeValuesError)
    assert error.component_type == NewQbAttribute
    assert error.map_uri_safe_values_to_conflicting_labels == {"a-b": {"A B", "A.B"}}


def test_conflict_existing_attribute_value_uri_values_error():
    """
    Test that a validation error is raised when the user defines new attribute value labels (on an existing attribute)
     which are distinct but map to the same URI-safe value.
    """
    data = pd.DataFrame(
        {
            "New Dimension": ["A", "B"],
            "Existing Attribute": ["A B", "A.B"],
            "Value": [2, 2],
        }
    )

    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=data,
        columns=[
            QbColumn(
                "New Dimension",
                NewQbDimension.from_data("New Dimension", data["New Dimension"]),
            ),
            QbColumn(
                "Existing Attribute",
                ExistingQbAttribute(
                    "http://example.com/attributes/existing-attribute",
                    [NewQbAttributeValue("A B"), NewQbAttributeValue("A.B")],
                ),
            ),
            QbColumn(
                "Value",
                QbObservationValue(
                    NewQbMeasure("Some Measure"),
                    NewQbUnit("Some Unit"),
                ),
            ),
        ],
    )
    error = _get_single_validation_error_for_qube(qube)
    assert isinstance(error, ConflictingUriSafeValuesError)
    assert error.component_type == ExistingQbAttribute
    assert error.map_uri_safe_values_to_conflicting_labels == {"a-b": {"A B", "A.B"}}


def test_conflict_new_units_uri_values_error():
    """
    Test that a validation error is raised when the user defines new units which are distinct but map to the
     same URI-safe value.
    """
    data = pd.DataFrame(
        {
            "New Dimension": ["A", "B"],
            "Units": ["A B", "A.B"],
            "Value": [2, 2],
        }
    )

    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=data,
        columns=[
            QbColumn(
                "New Dimension",
                NewQbDimension.from_data("New Dimension", data["New Dimension"]),
            ),
            QbColumn(
                "Units",
                QbMultiUnits.new_units_from_data(data["Units"]),
            ),
            QbColumn(
                "Value",
                QbObservationValue(NewQbMeasure("Some Measure")),
            ),
        ],
    )
    error = _get_single_validation_error_for_qube(qube)
    assert isinstance(error, ConflictingUriSafeValuesError)
    assert error.component_type == QbMultiUnits
    assert error.map_uri_safe_values_to_conflicting_labels == {"a-b": {"A B", "A.B"}}


def test_conflict_new_measures_uri_values_error():
    """
    Test that a validation error is raised when the user defines new measures which are distinct but map to the
     same URI-safe value.
    """
    data = pd.DataFrame(
        {
            "New Dimension": ["A", "B"],
            "Measures": ["A B", "A.B"],
            "Value": [2, 2],
        }
    )

    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=data,
        columns=[
            QbColumn(
                "New Dimension",
                NewQbDimension.from_data("New Dimension", data["New Dimension"]),
            ),
            QbColumn(
                "Measures",
                QbMultiMeasureDimension.new_measures_from_data(data["Measures"]),
            ),
            QbColumn(
                "Value",
                QbObservationValue(unit=NewQbUnit("Some Unit")),
            ),
        ],
    )
    error = _get_single_validation_error_for_qube(qube)
    assert isinstance(error, ConflictingUriSafeValuesError)
    assert error.component_type == QbMultiMeasureDimension
    assert error.map_uri_safe_values_to_conflicting_labels == {"a-b": {"A B", "A.B"}}


def test_pivoted_validation_multiple_measure_columns():
    """
    First scenario where there aare more then one or more measure columns defined

    """
    metadata = CatalogMetadata(title="cube_name", identifier="identifier")
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Some Attribute": ["attr-a", "attr-b", "attr-c"],
            "Some Measure": ["abc", "def", "ghi"],
            "Some Obs Val": [1, 2, 3],
            "Some Other Obs Val": [2, 4, 6],
        }
    )
    columns = [
        QbColumn(
            "Some Dimension",
            NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
        ),
        QbColumn(
            "Some Attribute",
            NewQbAttribute.from_data(
                "Some Attribute",
                data["Some Attribute"],
                observed_value_col_title="Some Obs Val",
            ),
        ),
        QbColumn(
            "Some Measure",
            QbMultiMeasureDimension.new_measures_from_data(data["Some Measure"]),
        ),
        QbColumn(
            "Some Obs Val",
            QbObservationValue(NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")),
        ),
        QbColumn(
            "Some Other Obs Val",
            QbObservationValue(
                NewQbMeasure("Some Other Measure"), NewQbUnit("Some Unit")
            ),
        ),
    ]

    cube = Cube(metadata=metadata, data=data, columns=columns)
    validate_with_environ(cube, BothMeasureTypesDefinedError)


def test_pivoted_validation_obs_value__error():
    """
    This scenario will test a cube with the observation column will not have a measure defined
    """
    metadata = CatalogMetadata(title="cube_name", identifier="identifier")
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Some Attribute": ["attr-a", "attr-b", "attr-c"],
            "Some Obs Val": [1, 2, 3],
            "Some Other Obs Val": [2, 4, 6],
        }
    )
    columns = [
        QbColumn(
            "Some Dimension",
            NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
        ),
        QbColumn(
            "Some Attribute",
            NewQbAttribute.from_data(
                "Some Attribute",
                data["Some Attribute"],
                observed_value_col_title="Some Obs Val",
            ),
        ),
        QbColumn(
            "Some Obs Val",
            QbObservationValue(NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")),
        ),
        QbColumn(
            "Some Other Obs Val",
            QbObservationValue(NewQbUnit("Some Unit")),
        ),
    ]

    cube = Cube(metadata=metadata, data=data, columns=columns)

    error = _get_single_validation_error_for_qube(cube)
    validate_with_environ(
        cube,
    )


def test_pivoted_validation_obs_value_no_unit_defined_error():
    """
    This scenario will test a cube that has an observation value column does not
    have a unit defined and there does not exist a units column which is linked to this obs val column
    """
    metadata = CatalogMetadata(title="cube_name", identifier="identifier")
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Some Attribute": ["attr-a", "attr-b", "attr-c"],
            "Some Obs Val": [1, 2, 3],
            "Some Other Obs Val": [2, 4, 6],
        }
    )
    columns = [
        QbColumn(
            "Some Dimension",
            NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
        ),
        QbColumn(
            "Some Attribute",
            NewQbAttribute.from_data(
                "Some Attribute",
                data["Some Attribute"],
                observed_value_col_title="Some Obs Val",
            ),
        ),
        QbColumn(
            "Some Obs Val",
            QbObservationValue(NewQbMeasure("Some Measure")),
        ),
        QbColumn(
            "Some Other Obs Val",
            QbObservationValue(NewQbMeasure("Some Other Measure")),
        ),
    ]

    cube = Cube(metadata=metadata, data=data, columns=columns)

    error = _get_single_validation_error_for_qube(cube)
    assert isinstance(error, ConflictingUriSafeValuesError)


def test_pivoted_validation_unit_column_not_linked_error():
    """
    This scenario will test a cube that has a units or attribute column has been defined without being linked to an obs val column
    """
    metadata = CatalogMetadata(title="cube_name", identifier="identifier")
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Some Attribute": ["attr-a", "attr-b", "attr-c"],
            "Some Obs Val": [1, 2, 3],
            "Some Other Obs Val": [2, 4, 6],
        }
    )
    columns = [
        QbColumn(
            "Some Dimension",
            NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
        ),
        QbColumn(
            "Some Attribute",
            NewQbAttribute.from_data("Some Attribute", data["Some Attribute"]),
        ),
        QbColumn(
            "Some Obs Val",
            QbObservationValue(NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")),
        ),
        QbColumn(
            "Some Other Obs Val",
            QbObservationValue(
                NewQbMeasure("Some Other Measure"), NewQbUnit("Some Unit")
            ),
        ),
    ]

    cube = Cube(metadata=metadata, data=data, columns=columns)

    error = _get_single_validation_error_for_qube(cube)
    assert isinstance(error, ConflictingUriSafeValuesError)


def test_pivoted_validation_obs_calumn_doesnt_exist():
    """
    This scenario will test the cube with units or attribute column is defined for which obs val column doesn't appear to exist.
    """

    metadata = CatalogMetadata(title="cube_name", identifier="identifier")
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Some Attribute": ["attr-a", "attr-b", "attr-c"],
            "Some Obs Val": [1, 2, 3],
            "Some Other Obs Val": [2, 4, 6],
        }
    )
    columns = [
        QbColumn(
            "Some Dimension",
            NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
        ),
        QbColumn(
            "Some Attribute",
            NewQbAttribute.from_data(
                "Some Attribute",
                data["Some Attribute"],
                observed_value_col_title="Not Obs Val",
            ),
        ),
        QbColumn(
            "Some Obs Val",
            QbObservationValue(NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")),
        ),
        QbColumn(
            "Some Other Obs Val",
            QbObservationValue(
                NewQbMeasure("Some Other Measure"), NewQbUnit("Some Unit")
            ),
        ),
    ]

    cube = Cube(metadata=metadata, data=data, columns=columns)

    error = _get_single_validation_error_for_qube(cube)
    assert isinstance(error, ConflictingUriSafeValuesError)


def test_pivoted_validation_link_attribe_to_non_obs_column():
    """
    This scenarion will produce an error where the units or attribute column is defined in which
     the linked obs val column isn't actually an observations column.
    """

    metadata = CatalogMetadata(title="cube_name", identifier="identifier")
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Some Attribute": ["attr-a", "attr-b", "attr-c"],
            "Some Obs Val": [1, 2, 3],
            "Some Other Obs Val": [2, 4, 6],
        }
    )
    columns = [
        QbColumn(
            "Some Dimension",
            NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
        ),
        QbColumn(
            "Some Attribute",
            NewQbAttribute.from_data(
                "Some Attribute",
                data["Some Attribute"],
                observed_value_col_title="Some Dimension",
            ),
        ),
        QbColumn(
            "Some Obs Val",
            QbObservationValue(NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")),
        ),
        QbColumn(
            "Some Other Obs Val",
            QbObservationValue(
                NewQbMeasure("Some Other Measure"), NewQbUnit("Some Unit")
            ),
        ),
    ]

    cube = Cube(metadata=metadata, data=data, columns=columns)

    error = _get_single_validation_error_for_qube(cube)
    assert isinstance(error, ConflictingUriSafeValuesError)


def test_pivoted_validation_measure_dupication():

    """
    This scenario will produce an arror for each pivoted multi-measure observation column has a unique measure.
     i.e. the same measure cannot be used twice in the same data set.
    """
    metadata = CatalogMetadata(title="cube_name", identifier="identifier")
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Some Attribute": ["attr-a", "attr-b", "attr-c"],
            "Some Obs Val": [1, 2, 3],
            "Some Other Obs Val": [2, 4, 6],
        }
    )
    columns = [
        QbColumn(
            "Some Dimension",
            NewQbDimension.from_data("Some Dimension", data["Some Dimension"]),
        ),
        QbColumn(
            "Some Attribute",
            NewQbAttribute.from_data(
                "Some Attribute",
                data["Some Attribute"],
                observed_value_col_title="Some Obs Val",
            ),
        ),
        QbColumn(
            "Some Obs Val",
            QbObservationValue(NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")),
        ),
        QbColumn(
            "Some Other Obs Val",
            QbObservationValue(
                ExistingQbMeasure("Some Measure"), NewQbUnit("Some Unit")
            ),
        ),
    ]

    cube = Cube(metadata=metadata, data=data, columns=columns)

    error = _get_single_validation_error_for_qube(cube)
    assert isinstance(error, ConflictingUriSafeValuesError)


def validate_with_environ(cube, expected_error):
    try:
        os.environ["PIVOTED_MULTI_MEASURE"] = "true"
        error = _get_single_validation_error_for_qube(cube)
        assert isinstance(error, expected_error)
    finally:
        del os.environ["PIVOTED_MULTI_MEASURE"]


def _get_single_validation_error_for_qube(qube: QbCube) -> ValidationError:
    errors = qube.validate() + validate_qb_component_constraints(qube)
    assert_num_validation_errors(errors, 1)
    return errors[0]


if __name__ == "__main__":
    pytest.main()
