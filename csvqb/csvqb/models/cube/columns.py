from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, List


from csvqb.models.validationerror import ValidationError


class CsvColumn(ABC):
    csv_column_title: str

    def __init__(self, csv_column_title: str):
        self.csv_column_title = csv_column_title

    @abstractmethod
    def validate(self, column_data: Optional[pd.Series]) -> List[ValidationError]:
        pass


class SuppressedCsvColumn(CsvColumn):
    """
        A column which is only defined in the CSV and should not be propagated.
    """

    def __init__(self, csv_column_title: str):
        CsvColumn.__init__(self, csv_column_title)

    def validate(self, column_data: pd.Series) -> List[ValidationError]:
        return []
