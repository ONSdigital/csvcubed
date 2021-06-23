from datetime import datetime
from typing import List, Optional, NewType, Set
import pandas as pd
from dateutil import parser


from csvqb.utils.dict import get_from_dict_ensure_exists, get_with_func_or_none
from csvqb.models.validationerror import ValidationError
from .columns import CsvColumn


URI = NewType('URI', str)


class CubeMetadata:
    base_uri: str
    dataset_identifier: str

    title: str
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

    def __init__(self, config: dict = {}):
        self.base_uri = config.get("baseUri", "http://gss-data")  # todo: check
        self.dataset_identifier = get_from_dict_ensure_exists(config, "id")

        self.title = get_from_dict_ensure_exists(config, "title")
        self.summary = config.get("summary")
        self.description = config.get("description")
        self.creator = get_with_func_or_none(config, "creator", URI)
        self.publisher = get_with_func_or_none(config, "publisher", URI)
        self.issued = get_with_func_or_none(config, "published", parser.parse)
        self.themes = config.get("families", [])
        self.keywords = config.get("keywords", [])
        self.landing_page = config.get("landingPage")
        self.license = config.get("license")
        self.public_contact_point = config.get("contactUri")

    def validate(self) -> List[ValidationError]:
        raise Exception("Not implemented yet.")


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
        # self.metadata.validate() # todo: uncomment this when implemented
        return self._validate_columns()

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
                column_data = self.data[column_data]

            errors += col.validate(column_data)
        return errors
