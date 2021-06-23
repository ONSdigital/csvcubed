from typing import Optional, List
from abc import ABC

import pandas as pd

from csvqb.utils.uri import uri_safe
from .datastructuredefinition import QbDataStructureDefinition
from csvqb.models.cube.qb.components.codelist import QbCodeList, ExistingQbCodeList, NewQbCodeList, NewQbConcept
from csvqb.models.validationerror import ValidationError


class QbDimension(QbDataStructureDefinition, ABC):
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

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this


class NewQbDimension(QbDimension):
    label: str
    uri_safe_identifier: str
    description: Optional[str]
    parent_dimension_uri: Optional[str]
    source_uri: Optional[str]

    def __init__(self,
                 label: str,
                 description: Optional[str] = None,
                 uri_safe_identifier: Optional[str] = None,
                 code_list: Optional[QbCodeList] = None,
                 parent_dimension_uri: Optional[str] = None,
                 source_uri: Optional[str] = None):
        QbDimension.__init__(self, code_list)
        self.label = label
        self.description = description
        self.uri_safe_identifier = uri_safe_identifier if uri_safe_identifier is not None else uri_safe(label)
        self.parent_dimension_uri = parent_dimension_uri
        self.source_uri = source_uri

    @staticmethod
    def from_data(label: str,
                  data: pd.Series,
                  description: Optional[str] = None,
                  uri_safe_identifier: Optional[str] = None,
                  parent_dimension_uri: Optional[str] = None,
                  source_uri: Optional[str] = None) -> "NewQbDimension":
        concepts = {NewQbConcept(c, c) for c in set(data)}
        return NewQbDimension(label,
                              description=description,
                              uri_safe_identifier=uri_safe_identifier,
                              code_list=NewQbCodeList(concepts),
                              parent_dimension_uri=parent_dimension_uri,
                              source_uri=source_uri)

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this
