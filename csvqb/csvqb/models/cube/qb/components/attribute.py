from typing import Optional, List
from abc import ABC

import pandas as pd

from csvqb.utils.uri import uri_safe
from .datastructuredefinition import QbDataStructureDefinition
from csvqb.models.validationerror import ValidationError


class QbAttribute(QbDataStructureDefinition, ABC):
    pass


class ExistingQbAttribute(QbAttribute):
    attribute_uri: str

    def __init__(self, uri: str):
        self.attribute_uri = uri

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this


class NewQbAttribute(QbAttribute):
    label: str
    uri_safe_identifier: str
    description: Optional[str]
    parent_attribute_uri: Optional[str]
    source_uri: Optional[str]

    def __init__(self,
                 label: str,
                 uri_safe_identifier: Optional[str] = None,
                 description: Optional[str] = None,
                 parent_attribute_uri: Optional[str] = None,
                 source_uri: Optional[str] = None):
        self.label = label
        self.uri_safe_identifier = uri_safe_identifier if uri_safe_identifier is not None else uri_safe(label)
        self.description = description
        self.parent_attribute_uri = parent_attribute_uri
        self.source_uri = source_uri

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this

