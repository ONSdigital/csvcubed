from datetime import datetime
from typing import List, Optional, Set
import pandas as pd
from dateutil import parser


from csvqb.utils.dict import get_from_dict_ensure_exists, get_with_func_or_none
from csvqb.models.validationerror import ValidationError
from .columns import CsvColumn
from ..rdf import URI


class CubeMetadata:
    dataset_identifier: str
    title: str
    base_uri: str
    summary: Optional[str]
    description: Optional[str]
    creator: Optional[URI]
    publisher: Optional[URI]
    issued: Optional[datetime]
    # modified: datetime # Should modified be in here or be automatically updated by the script?
    themes: List[str]
    keywords: List[str]
    landing_page: Optional[URI]
    license: Optional[URI]
    public_contact_point: Optional[URI]

    def __init__(self,
                 dataset_identifier: URI,
                 title: str,
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
        self.base_uri = "http://gss-data.org.uk/" if base_uri is None else base_uri
        self.dataset_identifier = dataset_identifier
        self.title = title
        self.summary = summary
        self.description = description
        self.creator = creator
        self.publisher = publisher
        self.issued = issued
        self.themes = themes
        self.keywords = keywords
        self.landing_page = landing_page
        self.license = license
        self.public_contact_point = public_contact_point

    @staticmethod
    def from_dict(config: dict) -> "CubeMetadata":
        return CubeMetadata(
            URI(get_from_dict_ensure_exists(config, "id")),
            get_from_dict_ensure_exists(config, "title"),
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
    metadata: CubeMetadata
    columns: List[CsvColumn]
    data: Optional[pd.DataFrame]

    def __init__(self,
                 metadata: CubeMetadata,
                 data: Optional[pd.DataFrame] = None,
                 columns: List[CsvColumn] = []):
        self.metadata = metadata
        self.data = data
        self.columns = columns

    def validate(self) -> List[ValidationError]:
        errors = self.metadata.validate()
        errors += self._validate_columns()
        return errors

    def _validate_columns(self) -> List[ValidationError]:
        # todo: If no columns are defined give a warning?
        errors = self._validate_columns_unique_and_in_data()
        return errors

    def _validate_columns_unique_and_in_data(self):
        errors: List[ValidationError] = []
        existing_col_titles: Set[str] = set()
        for col in self.columns:
            if col.csv_column_title in existing_col_titles:
                errors.append(ValidationError(f"Duplicate column title '{col.csv_column_title}'"))

            column_data = None
            if self.data is not None:
                if col.csv_column_title not in self.data.columns:
                    errors.append(ValidationError(f"Column '{col.csv_column_title}' not found in data provided."))
                column_data = self.data[col.csv_column_title]

            errors += col.validate(column_data)
        return errors
