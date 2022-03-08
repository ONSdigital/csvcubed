"""
Cube
----
"""
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Set, TypeVar, Generic
import pandas as pd

from csvcubed.models.validationerror import (
    ValidationError,
)

from csvcubed.models.cube.validationerrors import (
    DuplicateColumnTitleError,
    ColumnNotFoundInDataError,
    MissingColumnDefinitionError,
    ColumnValidationError,
)
from csvcubed.models.cube.columns import CsvColumn

from csvcubed.models.cube.catalog import CatalogMetadataBase
from csvcubed.models.pydanticmodel import PydanticModel
from csvcubed.utils.log import log_exception


_logger = logging.getLogger(__name__)

TMetadata = TypeVar("TMetadata", bound=CatalogMetadataBase, covariant=True)


@dataclass
class Cube(Generic[TMetadata], PydanticModel):
    metadata: TMetadata
    data: Optional[pd.DataFrame] = field(default=None, repr=False)
    columns: List[CsvColumn] = field(default_factory=lambda: [], repr=False)

    def validate(self) -> List[ValidationError]:
        errors: List[ValidationError] = []
        try:
            errors += self.pydantic_validation()
            errors += self._validate_columns()
        except Exception as e:
            log_exception(_logger, e)
            errors.append(ValidationError(str(e)))
            errors.append(
                ValidationError("An error occurred and validation Failed to Complete")
            )

        return errors

    @staticmethod
    def _get_validation_error_for_exception_in_col(
        csv_column_title: str, error: Exception
    ) -> ColumnValidationError:
        log_exception(_logger, error)
        return ColumnValidationError(csv_column_title, error)

    def _validate_columns(self) -> List[ValidationError]:
        errors: List[ValidationError] = []
        existing_col_titles: Set[str] = set()
        for col in self.columns:
            try:
                if col.csv_column_title in existing_col_titles:
                    errors.append(DuplicateColumnTitleError(col.csv_column_title))
                else:
                    existing_col_titles.add(col.csv_column_title)

                maybe_column_data = None
                if self.data is not None:
                    if col.csv_column_title in self.data.columns:
                        maybe_column_data = self.data[col.csv_column_title]
                    else:
                        errors.append(ColumnNotFoundInDataError(col.csv_column_title))

                if maybe_column_data is not None:
                    errors += col.validate_data(maybe_column_data)
            except Exception as e:
                errors.append(
                    self._get_validation_error_for_exception_in_col(
                        col.csv_column_title, e
                    )
                )

        if self.data is not None:
            defined_column_titles = [c.csv_column_title for c in self.columns]
            for column in list(self.data.columns):
                try:
                    column = str(column)
                    if column not in defined_column_titles:
                        errors.append(MissingColumnDefinitionError(column))
                except Exception as e:
                    errors.append(
                        self._get_validation_error_for_exception_in_col(column, e)
                    )

        return errors
