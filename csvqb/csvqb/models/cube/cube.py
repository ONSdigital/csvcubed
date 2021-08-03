"""
Cube
----
"""
from dataclasses import dataclass, field
from typing import List, Optional, Set, TypeVar, Generic
import pandas as pd

from csvqb.models.validationerror import ValidationError
from .columns import CsvColumn
from csvqb.models.cube.catalog import CatalogMetadataBase
from csvqb.inputs import pandas_input_to_columnar
from ..pydanticmodel import PydanticModel

TMetadata = TypeVar("TMetadata", bound=CatalogMetadataBase, covariant=True)


@dataclass
class Cube(Generic[TMetadata], PydanticModel):
    metadata: TMetadata
    data: Optional[pd.DataFrame] = field(default=None, repr=False)
    columns: List[CsvColumn] = field(default_factory=lambda: [], repr=False)

    def validate(self) -> List[ValidationError]:
        errors = self.pydantic_validation()
        try:
            errors += self._validate_columns()
        except Exception as e:
            errors.append(ValidationError(str(e)))

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

            errors += col.validate_data(maybe_column_data)

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
