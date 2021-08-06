from typing import List

import pandas as pd
import pytest

from csvqb.models.cube import *


def test_column_not_configured_error():
    """
    If the CSV data contains a column which is not defined, we get an error.
    """

    data = pd.DataFrame({"Some Dimension": ["A", "B", "C"]})

    metadata = CatalogMetadata("Some Dataset")
    columns = []
    cube = Cube(metadata, data, columns)
    validation_errors = cube.validate()

    assert len(validation_errors) == 1
    error = validation_errors[0]
    assert isinstance(error, MissingColumnDefinitionError)
    assert error.csv_column_title == "Some Dimension"
    assert "Column 'Some Dimension'" in error.message


def test_column_title_wrong_error():
    """
    If the Cube object contains a column title which is not defined in the CSV data, we get an error.
    """

    data = pd.DataFrame()

    metadata = CatalogMetadata("Some Dataset")
    columns: List[CsvColumn] = [SuppressedCsvColumn("Some Column Title")]
    cube = Cube(metadata, data, columns)
    validation_errors = cube.validate()

    assert len(validation_errors) == 1
    error = validation_errors[0]
    assert isinstance(error, ColumnNotFoundInDataError)
    assert error.csv_column_title == "Some Column Title"
    assert "Column 'Some Column Title'" in error.message


def test_two_column_same_title():
    """
    If cube with two columns with the same title is defined, we get an error
    """
    data = pd.DataFrame(
        {"Some Dimension": ["A", "B", "C"], "Some Dimension": ["A", "B", "C"]}
    )

    metadata = CatalogMetadata("Some Dataset")
    columns: List[CsvColumn] = [
        SuppressedCsvColumn("Some Dimension"),
        SuppressedCsvColumn("Some Dimension"),
    ]

    cube = Cube(metadata, data, columns)
    validation_errors = cube.validate()

    assert len(validation_errors) == 1
    error = validation_errors[0]
    assert isinstance(error, DuplicateColumnTitleError)
    assert error.csv_column_title == "Some Dimension"
    assert "Duplicate column title 'Some Dimension'" == error.message


if __name__ == "__main__":
    pytest.main()
