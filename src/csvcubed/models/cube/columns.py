"""
CSV Column Definitions
----------------------
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvcubed.inputs import PandasDataTypes
from csvcubed.models.pydanticmodel import PydanticModel
from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.models.validatedmodel import ValidationFunction
from csvcubed.models.validationerror import ValidationError
from csvcubed.utils.validations import validate_str_type


@dataclass
class CsvColumn(PydanticModel, UriIdentifiable, ABC):
    csv_column_title: str

    def get_identifier(self) -> str:
        return self.csv_column_title

    @abstractmethod
    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        pass

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {"csv_column_title": validate_str_type}


@dataclass
class SuppressedCsvColumn(CsvColumn):
    """
    A column which is only defined in the CSV and should not be propagated.
    """

    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {
            **CsvColumn._get_validations(self),
            **UriIdentifiable._get_validations(self),
        }
