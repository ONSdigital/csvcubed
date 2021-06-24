from typing import Optional, List, Dict, Any
from abc import ABC

import pandas as pd

from csvqb.utils.uri import uri_safe
from .datastructuredefinition import ColumnarQbDataStructureDefinition
from csvqb.models.validationerror import ValidationError


class QbAttribute(ColumnarQbDataStructureDefinition, ABC):
    pass


class ExistingQbAttribute(QbAttribute):

    def __init__(self, uri: str):
        self.attribute_uri: str = uri

    def __str__(self) -> str:
        return f"ExistingQbAttribute('{self.attribute_uri}')"

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this


class NewQbAttribute(QbAttribute):

    def __init__(self,
                 label: str,
                 uri_safe_identifier: Optional[str] = None,
                 description: Optional[str] = None,
                 parent_attribute_uri: Optional[str] = None,
                 source_uri: Optional[str] = None):
        self.label: str = label
        self.uri_safe_identifier: str = uri_safe_identifier if uri_safe_identifier is not None else uri_safe(label)
        self.description: Optional[str] = description
        self.parent_attribute_uri: Optional[str] = parent_attribute_uri
        self.source_uri: Optional[str] = source_uri

    def __str__(self) -> str:
        return f"NewQbAttribute('{self.label}')"

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this
