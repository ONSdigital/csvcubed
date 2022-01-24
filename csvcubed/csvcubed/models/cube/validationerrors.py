"""
Cube Validation Errors
----------------------
"""
from collections.abc import Set
from dataclasses import dataclass

from csvcubed.models.validationerror import SpecificValidationError


@dataclass
class DuplicateColumnTitleError(SpecificValidationError):
    """
    An error to inform the user that they have defined two instances of the same column.
    """

    csv_column_title: str

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/dupe-col'

    def __post_init__(self):
        self.message = f"Duplicate column title '{self.csv_column_title}'"


@dataclass
class ColumnNotFoundInDataError(SpecificValidationError):
    """
    An error to inform the user that they have defined a column which cannot be found in the provided data.
    """

    csv_column_title: str
    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/col-not-found-in-dat'

    def __post_init__(self):
        self.message = f"Column '{self.csv_column_title}' not found in data provided."


@dataclass
class MissingColumnDefinitionError(SpecificValidationError):
    """
    An error to inform the user that there is a column in their data that does not have a mapping specified.
    """

    csv_column_title: str

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/mis-col-def'

    def __post_init__(self):
        self.message = (
            f"Column '{self.csv_column_title}' does not have a mapping defined."
        )


@dataclass
class ColumnValidationError(SpecificValidationError):
    """
    An error to inform the user that there a general exception occurred when attempting to validate a column.
    """

    csv_column_title: str
    error: Exception

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/col-valid'

    def __post_init__(self):
        self.message = f"An exception occurred when validating column '{self.csv_column_title}': {self.error}."


@dataclass
class ObservationValuesMissing(SpecificValidationError):
    """
    An error to inform the user that there are missing observation values in their data for which they have not set
    an `sdmxa:obsStatus`.
    """

    csv_column_title: str
    row_numbers: Set[int]

    @classmethod
    def get_error_url(cls) -> str:
        return 'http://purl.org/csv-cubed/err/obsv-val-mis'

    def __post_init__(self):
        row_nums_str = ", ".join([str(i) for i in sorted(self.row_numbers)])
        self.message = f"Missing value(s) found for '{self.csv_column_title}' in row(s) {row_nums_str}."
