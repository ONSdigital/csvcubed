from datetime import datetime
from typing import List, Optional, Set
import pandas as pd


from csvqb.utils.uri import uri_safe
from csvqb.models.validationerror import ValidationError
from .columns import CsvColumn
from ..rdf import URI
from csvqb.inputs import pandas_input_to_columnar


class CubeMetadata:

    def __init__(self,
                 title: str,
                 uri_safe_identifier: Optional[str] = None,
                 summary: Optional[str] = None,
                 description: Optional[str] = None,
                 creator: Optional[URI] = None,
                 publisher: Optional[URI] = None,
                 issued: Optional[datetime] = None,
                 themes: List[str] = [],
                 keywords: List[str] = [],
                 landing_page: Optional[URI] = None,
                 license: Optional[URI] = None,
                 public_contact_point: Optional[URI] = None):
        self.title: str = title
        self.uri_safe_identifier: str = uri_safe(title) if uri_safe_identifier is None else uri_safe_identifier
        self.summary: Optional[str] = summary
        self.description: Optional[str] = description
        self.creator: Optional[URI] = creator
        self.publisher: Optional[URI] = publisher
        self.issued: Optional[datetime] = issued
        self.themes: List[str] = themes
        self.keywords: List[str] = keywords
        self.landing_page: Optional[URI] = landing_page
        self.license: Optional[URI] = license
        self.public_contact_point: Optional[URI] = public_contact_point

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this


class Cube:
    def __init__(self,
                 metadata: CubeMetadata,
                 data: Optional[pd.DataFrame] = None,
                 columns: List[CsvColumn] = []):
        self.metadata: CubeMetadata = metadata
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
                errors.append(ValidationError(f"Duplicate column title '{col.csv_column_title}'"))

            maybe_column_data = None
            if self.data is not None:
                if col.csv_column_title in self.data.columns:
                    maybe_column_data = self.data[col.csv_column_title]
                else:
                    errors.append(ValidationError(f"Column '{col.csv_column_title}' not found in data provided."))

            errors += col.validate(pandas_input_to_columnar(maybe_column_data))

        if self.data is not None:
            defined_column_titles = [c.csv_column_title for c in self.columns]
            for column in list(self.data.columns):
                if column not in defined_column_titles:
                    errors.append(ValidationError(f"Column '{column}' does not have a mapping defined."))

        return errors
