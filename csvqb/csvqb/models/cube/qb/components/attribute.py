from typing import Optional, List
from abc import ABC

import pandas as pd

from .component import QbComponent
from csvqb.models.validationerror import ValidationError


class QbAttribute(QbComponent, ABC):
    pass


class ExistingQbAttribute(QbAttribute):
    uri: str

    def __init__(self, uri: str):
        self.uri = uri

    def validate(self) -> bool:
        raise Exception("Not implemented yet")

    def validate_data(self, data: pd.Series) -> bool:
        raise Exception("Not implemented yet")


class NewQbAttribute(QbAttribute):
    label: str
    description: Optional[str]
    parent_attribute_uri: Optional[str]
    source_uri: Optional[str]

    def __init__(self,
                 label: str,
                 description: Optional[str] = None,
                 parent_attribute_uri: Optional[str] = None,
                 source_uri: Optional[str] = None):
        self.label = label
        self.description = description
        self.parent_attribute_uri = parent_attribute_uri
        self.source_uri = source_uri

    def validate(self) -> List[ValidationError]:
        raise Exception("Not implemented yet")

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        raise Exception("Not implemented yet")


class QbUnitAttribute(ExistingQbAttribute):
    unit_template_uri: str

    def __init__(self, unit_template_uri: str):
        ExistingQbAttribute.__init__(self, "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure")
        self.unit_template_uri = unit_template_uri
