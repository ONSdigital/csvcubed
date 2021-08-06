from dataclasses import dataclass

from csvqb.models.validationerror import SpecificValidationError


@dataclass
class DuplicateColumnTitleError(SpecificValidationError):
    """
    An error to inform the user that they have defined two instances of the same column.
    """

    csv_column_title: str

    def __post_init__(self):
        self.message = f"Duplicate column title '{self.csv_column_title}'"


@dataclass
class ColumnNotFoundInDataError(SpecificValidationError):
    """
    An error to inform the user that they have defined a column which cannot be found in the provided data.
    """

    csv_column_title: str

    def __post_init__(self):
        self.message = f"Column '{self.csv_column_title}' not found in data provided."


@dataclass
class MissingColumnDefinitionError(SpecificValidationError):
    """
    An error to inform the user that there is a column in their data that does not have a mapping specified.
    """

    csv_column_title: str

    def __post_init__(self):
        self.message = (
            f"Column '{self.csv_column_title}' does not have a mapping defined."
        )
