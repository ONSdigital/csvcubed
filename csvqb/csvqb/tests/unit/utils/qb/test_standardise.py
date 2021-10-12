import pandas as pd
import pytest
from pandas.core.arrays.categorical import Categorical

from csvqb.models.cube import *
from csvqb.utils.qb.standardise import (
    ensure_qbcube_data_is_categorical,
    convert_data_values_to_uri_safe_values,
)


def test_qbcube_data_is_categorical():
    """
    Ensure that when we convert a QbCube's dataframe columns to categorical, it is done for the appropriate columns.
    """
    data = pd.DataFrame(
        {
            "Some Dimension": ["a", "b", "c"],
            "Some Resource Attribute": ["r-a", "r-b", "r-c"],
            "Some Literal Attribute": ["l-a", "l-b", "l-c"],
            "Measure": ["meas-a", "meas-b", "meas-c"],
            "Unit": ["unit-a", "unit-b", "unit-c"],
            "Observed Value": [1, 2, 3],
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
                "Some Resource Attribute",
                NewQbAttribute.from_data(
                    "Some Resource Attribute", data["Some Resource Attribute"]
                ),
            ),
            QbColumn(
                "Some Literal Attribute",
                NewQbAttributeLiteral("string", "Some Literal Attribute"),
            ),
            QbColumn(
                "Measure",
                QbMultiMeasureDimension.new_measures_from_data(data["Measure"]),
            ),
            QbColumn("Unit", QbMultiUnits.new_units_from_data(data["Unit"])),
            QbColumn("Observed Value", QbMultiMeasureObservationValue()),
        ],
    )

    ensure_qbcube_data_is_categorical(cube)

    map_col_to_expected_categories = {
        "Some Dimension": {"a", "b", "c"},
        "Some Resource Attribute": {"r-a", "r-b", "r-c"},
        "Measure": {"meas-a", "meas-b", "meas-c"},
        "Unit": {"unit-a", "unit-b", "unit-c"},
    }
    expected_non_categorical_columns = {"Observed Value", "Some Literal Attribute"}

    for (column_name, expected_categories) in map_col_to_expected_categories.items():
        values = cube.data[column_name].values
        assert isinstance(values, Categorical)
        assert set(values.categories) == expected_categories

    for column_name in expected_non_categorical_columns:
        values = cube.data[column_name].values
        assert not isinstance(values, Categorical)


def test_convert_data_values_to_uri_safe_values():
    """
    Ensure that substituting labels with uri-safe-values works for all known components with appropriate mappings
    defined.
    """
    data = pd.DataFrame(
        {
            "Some Dimension": ["Value A", "Value B", "Value C"],
            "Some Resource Attribute": ["Resource A", "Resource B", "Resource C"],
            "Measure": ["Measure A", "Measure B", "Measure C"],
            "Unit": ["Unit A", "Unit B", "Unit C"],
            "Observed Value": [1, 2, 3],
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
                "Some Resource Attribute",
                NewQbAttribute.from_data(
                    "Some Resource Attribute", data["Some Resource Attribute"]
                ),
            ),
            QbColumn(
                "Measure",
                QbMultiMeasureDimension.new_measures_from_data(data["Measure"]),
            ),
            QbColumn("Unit", QbMultiUnits.new_units_from_data(data["Unit"])),
            QbColumn("Observed Value", QbMultiMeasureObservationValue()),
        ],
    )

    convert_data_values_to_uri_safe_values(cube)

    map_col_to_expected_values = {
        "Some Dimension": ["value-a", "value-b", "value-c"],
        "Some Resource Attribute": ["resource-a", "resource-b", "resource-c"],
        "Measure": ["measure-a", "measure-b", "measure-c"],
        "Unit": ["unit-a", "unit-b", "unit-c"],
    }

    for (column_name, expected_values) in map_col_to_expected_values.items():
        values = list(cube.data[column_name].values)
        assert values == expected_values


def test_convert_data_values_to_uri_safe_values_missing_value_mapping():
    """
    Ensure that when a (label => uri-safe-value) mapping is left out, we get an exception when attempting to convert
    a cube's dataframe to uri safe values.
    """
    data = pd.DataFrame(
        {
            "Some Dimension": ["Value A", "Value B", "Value C"],
            "Observed Value": [1, 2, 3],
        }
    )
    cube = Cube(
        CatalogMetadata("Some Qube"),
        data,
        [
            QbColumn(
                "Some Dimension",
                NewQbDimension(
                    "Some Dimension",
                    code_list=NewQbCodeList(
                        CatalogMetadata("Some Code List"),
                        [
                            NewQbConcept("Value A", "value-a"),
                            NewQbConcept("Value B", "value-b"),
                            # deliberately leaving out `Value C` here to cause an exception.
                        ],
                    ),
                ),
            ),
            QbColumn(
                "Observed Value",
                QbSingleMeasureObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
    )

    with pytest.raises(ValueError) as err:
        convert_data_values_to_uri_safe_values(cube)
    assert (
        "Unable to find new category label for term 'Value C' in column 'Some Dimension'."
        in str(err)
    )


def test_qbcube_catagorical_numberic():
    """
    Ensure that when we convert a QbCube's dataframe columns to categorical, and it works for numeric
    """
    data = pd.DataFrame(
        {"Some Dimension": [2014, 2015, 2016], "Observed Value": [1, 2, 3]}
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
                "Observed Value",
                QbSingleMeasureObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
    )

    ensure_qbcube_data_is_categorical(cube)

    map_col_to_expected_categories = {
        "Some Dimension": {2014, 2015, 2016},
    }
    expected_non_categorical_columns = {"Observed Value"}

    for (column_name, expected_categories) in map_col_to_expected_categories.items():
        values = cube.data[column_name].values
        assert isinstance(values, Categorical)
        assert set(values.categories) == expected_categories

    for column_name in expected_non_categorical_columns:
        values = cube.data[column_name].values
        assert not isinstance(values, Categorical)


if __name__ == "__main__":
    pytest.main()
