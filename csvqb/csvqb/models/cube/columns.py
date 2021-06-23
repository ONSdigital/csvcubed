from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, List


from csvqb.utils.uri import uri_safe
from csvqb.models.validationerror import ValidationError


class CsvColumn(ABC):
    csv_column_title: str
    uri_safe_identifier: str

    def __init__(self, csv_column_title: str, uri_safe_identifier: Optional[str] = None):
        self.csv_column_title = csv_column_title
        self.uri_safe_identifier = uri_safe(csv_column_title) if uri_safe_identifier is None else uri_safe_identifier

    @abstractmethod
    def validate(self, column_data: Optional[pd.Series] = None) -> List[ValidationError]:
        pass


class SuppressedCsvColumn(CsvColumn):
    """
        A column which is only defined in the CSV and should not be propagated.
    """

    def __init__(self, csv_column_title: str, uri_safe_identifier: Optional[str] = None):
        CsvColumn.__init__(self, csv_column_title, uri_safe_identifier)

    def validate(self, column_data: Optional[pd.Series] = None) -> List[ValidationError]:
        return []  # TODO: implement this
