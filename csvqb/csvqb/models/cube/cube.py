from typing import List, Optional, Set, TypeVar, Generic
import pandas as pd

from csvqb.models.validationerror import ValidationError
from .columns import CsvColumn
from csvqb.models.cube.catalog import CatalogMetadataBase
from csvqb.inputs import pandas_input_to_columnar

TMetadata = TypeVar("TMetadata", bound=CatalogMetadataBase, covariant=True)


class Cube(Generic[TMetadata]):
    def __init__(
        self,
        metadata: TMetadata,
        data: Optional[pd.DataFrame] = None,
        columns: List[CsvColumn] = [],
    ):
        self.metadata: TMetadata = metadata
        self.data: Optional[pd.DataFrame] = data
        self.columns: List[CsvColumn] = columns

    def validate(self) -> List[ValidationError]:
        errors = self.metadata.validate()
        errors += self._validate_columns()
        return errors

    def _validate_columns(self) -> List[ValidationError]:
        errors: List[ValidationError] = []
        existing_col_titles: Set[str] = set()
        for col in self.columns:
            if col.csv_column_title in existing_col_titles:
                errors.append(
                    ValidationError(f"Duplicate column title '{col.csv_column_title}'")
                )
            else:
                existing_col_titles.add(col.csv_column_title)

            maybe_column_data = None
            if self.data is not None:
                if col.csv_column_title in self.data.columns:
                    maybe_column_data = self.data[col.csv_column_title]
                else:
                    errors.append(
                        ValidationError(
                            f"Column '{col.csv_column_title}' not found in data provided."
                        )
                    )

            errors += col.validate(pandas_input_to_columnar(maybe_column_data))

        if self.data is not None:
            defined_column_titles = [c.csv_column_title for c in self.columns]
            for column in list(self.data.columns):
                if column not in defined_column_titles:
                    errors.append(
                        ValidationError(
                            f"Column '{column}' does not have a mapping defined."
                        )
                    )

        return errors
