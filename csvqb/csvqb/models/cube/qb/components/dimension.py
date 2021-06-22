from typing import Optional
from abc import ABC

import pandas as pd

from .component import QbComponent
from ..codelist import QbCodeList, ExistingQbCodeList


class QbDimension(QbComponent, ABC):
    code_list: Optional[QbCodeList]

    def __init__(self, code_list: Optional[QbCodeList]):
        self.code_list = code_list


class ExistingQbDimension(QbDimension):
    dimension_uri: str
    range_uri: Optional[str]

    def __init__(self,
                 dimension_uri: str,
                 code_list: Optional[ExistingQbCodeList] = None,
                 range_uri: Optional[str] = None):
        QbDimension.__init__(self, code_list)
        self.dimension_uri = dimension_uri
        self.range_uri = range_uri

    def validate(self) -> bool:
        raise Exception("Not implemented yet")

    def validate_data(self, data: pd.Series) -> bool:
        raise Exception("Not implemented yet")


class NewQbDimension(QbDimension):
    label: str
    description: Optional[str]
    parent_dimension_uri: Optional[str]
    source_uri: Optional[str]

    def __init__(self,
                 label: str,
                 description: Optional[str] = None,
                 code_list: Optional[QbCodeList] = None,
                 parent_dimension_uri: Optional[str] = None,
                 source_uri: Optional[str] = None):
        QbDimension.__init__(self, code_list)
        self.label = label
        self.description = description
        self.parent_dimension_uri = parent_dimension_uri
        self.source_uri = source_uri

    def validate(self) -> bool:
        raise Exception("Not implemented yet")

    def validate_data(self, data: pd.Series) -> bool:
        raise Exception("Not implemented yet")


QbMeasureDimension = ExistingQbDimension("http://purl.org/linked-data/cube#measureType")

