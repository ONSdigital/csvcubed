from datetime import datetime
from typing import List, Optional, Set
import pandas as pd
from dateutil import parser


from csvqb.utils.dict import get_from_dict_ensure_exists, get_with_func_or_none
from csvqb.utils.uri import uri_safe
from csvqb.models.validationerror import ValidationError
from .columns import CsvColumn
from ..rdf import URI



class CubeMetadata:

    def __init__(self,
                 title: str,
                 uri_safe_identifier: Optional[str] = None,
                 base_uri: Optional[str] = None,
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
        self.base_uri: str = "http://gss-data.org.uk/" if base_uri is None else base_uri
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

    @staticmethod
    def from_dict(config: dict) -> "CubeMetadata":
        return CubeMetadata(
            get_from_dict_ensure_exists(config, "title"),
            uri_safe_identifier=get_from_dict_ensure_exists(config, "id"),
            base_uri=config.get("baseUri"),
            summary=config.get("summary"),
            description=config.get("description"),
            creator=get_with_func_or_none(config, "creator", URI),
            publisher=get_with_func_or_none(config, "publisher", URI),
            issued=get_with_func_or_none(config, "published", parser.parse),
            themes=config.get("families", []),
            keywords=config.get("keywords", []),
            landing_page=get_with_func_or_none(config, "landingPage", URI),
            license=config.get("license"),
            public_contact_point=get_with_func_or_none(config, "contactUri", URI)
        )

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

            errors += col.validate(maybe_column_data)

        if self.data is not None:
            defined_column_titles = [c.csv_column_title for c in self.columns]
            for column in self.data.columns:
                if column not in defined_column_titles:
                    errors.append(ValidationError(f"Column '{column}' does not have a mapping defined."))

        return errors
