from datetime import datetime
from typing import List, Optional, NewType, Set
import pandas as pd
from dateutil import parser


from columns import CsvColumn
from csvqb.utils.dict import get_from_dict_ensure_exists


URI = NewType('URI', str)


class CubeMetadata:
    base_uri: str
    dataset_identifier: str

    title: str
    summary: Optional[str]
    description: Optional[str]
    creator: Optional[URI]
    publisher: Optional[URI]
    issued: datetime
    # modified: datetime # Should modified be in here or be automatically updated by the script?
    themes: List[str]
    keywords: List[str]
    landing_page: Optional[URI]
    license: Optional[URI]
    public_contact_point: Optional[URI]

    def __init__(self, config: dict = {}):
        self.base_uri = get_from_dict_ensure_exists(config, "baseUri")  # todo: check
        self.dataset_identifier = get_from_dict_ensure_exists(config, "datasetIdentifier")  # todo: check

        self.title = get_from_dict_ensure_exists(config, "title")
        self.summary = config.get("summary")
        self.description = config.get("description")
        self.creator = URI(config.get("creator"))
        self.publisher = URI(config.get("publisher"))
        self.issued = parser.parse(config.get("published"))
        self.themes = config.get("families")
        self.keywords = config.get("keywords")
        self.landing_page = config.get("landingPage")
        self.license = config.get("license")
        self.public_contact_point = config.get("contactUri")

    def validate(self) -> bool:
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

    def validate(self) -> bool:
        # self.metadata.validate() # todo: uncomment this when implemented
        self.validate_columns()

    def validate_columns(self):
        # todo: If no columns are defined give a warning?
        existing_col_titles: Set[str] = set()
        for col in self.columns:
            if col.csv_column_title in existing_col_titles:
                raise Exception(f"Duplicate column title '{col.csv_column_title}'")

            if self.data is not None:
                if col.csv_column_title not in self.data.columns:
                    raise Exception(f"Column '{col.csv_column_title}' not found in data provided.")
                column_data = self.data[column_data]
            else:
                column_data = None

            col.validate(column_data)
