from typing import Optional, List
from abc import ABC
import pandas as pd


from csvqb.utils.uri import uri_safe
from csvqb.models.validationerror import ValidationError
from .attribute import ExistingQbAttribute


class QbUnit(ExistingQbAttribute, ABC):
    def __init__(self):
        ExistingQbAttribute.__init__(self, "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure")


class ExistingQbUnit(QbUnit):
    unit_uri: str

    def __init__(self, unit_uri: str):
        QbUnit.__init__(self)
        self.unit_uri = unit_uri

    def validate(self) -> List[ValidationError]:
        return ExistingQbAttribute.validate(self)  # todo: Add more validation here.

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return ExistingQbAttribute.validate_data(self, data)  # todo: Add more validation here.


class NewQbUnit(QbUnit):
    label: str
    uri_safe_identifier: str
    description: Optional[str]
    parent_unit_uri: Optional[str]
    source_uri: Optional[str]

    def __init__(self,
                 label: str,
                 uri_safe_identifier: Optional[str] = None,
                 description: Optional[str] = None,
                 parent_unit_uri: Optional[str] = None,
                 source_uri: Optional[str] = None):
        QbUnit.__init__(self)
        self.label = label
        self.uri_safe_identifier = uri_safe_identifier if uri_safe_identifier is not None else uri_safe(label)
        self.description = description
        self.parent_unit_uri = parent_unit_uri
        self.source_uri = source_uri

    def validate(self) -> List[ValidationError]:
        return ExistingQbAttribute.validate(self)  # todo: Add more validation here.

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return ExistingQbAttribute.validate_data(self, data)  # todo: Add more validation here.
