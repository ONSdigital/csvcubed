"""
Attributes
----------
"""
from typing import Optional, List
from abc import ABC

import pandas as pd

from csvqb.utils.uri import uri_safe
from .datastructuredefinition import ColumnarQbDataStructureDefinition
from .codelist import QbCodeList, NewQbCodeList
from csvqb.models.validationerror import ValidationError
from csvqb.inputs import PandasDataTypes
from csvqb.models.cube.csvqb.catalog import CatalogMetadata


class QbAttribute(ColumnarQbDataStructureDefinition, ABC):
    def __init__(self, is_required: bool):
        self.is_required: bool = is_required


class ExistingQbAttribute(QbAttribute):
    def __init__(self, uri: str, is_required: bool = False):
        QbAttribute.__init__(self, is_required)
        self.attribute_uri: str = uri

    def __str__(self) -> str:
        return f"ExistingQbAttribute('{self.attribute_uri}')"

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this


class NewQbAttribute(QbAttribute):
    def __init__(
        self,
        label: str,
        uri_safe_identifier: Optional[str] = None,
        description: Optional[str] = None,
        code_list: Optional[QbCodeList] = None,
        parent_attribute_uri: Optional[str] = None,
        source_uri: Optional[str] = None,
        is_required: bool = False,
    ):
        QbAttribute.__init__(self, is_required)
        self.label: str = label
        self.uri_safe_identifier: str = (
            uri_safe_identifier if uri_safe_identifier is not None else uri_safe(label)
        )
        self.description: Optional[str] = description
        self.code_list: Optional[QbCodeList] = code_list
        self.parent_attribute_uri: Optional[str] = parent_attribute_uri
        self.source_uri: Optional[str] = source_uri

    @staticmethod
    def from_data(
        label: str,
        data: PandasDataTypes,
        uri_safe_identifier: Optional[str] = None,
        description: Optional[str] = None,
        parent_attribute_uri: Optional[str] = None,
        source_uri: Optional[str] = None,
        is_required: bool = False,
    ):

        return NewQbAttribute(
            label,
            uri_safe_identifier=uri_safe_identifier,
            description=description,
            code_list=NewQbCodeList.from_data(CatalogMetadata(label), data),
            parent_attribute_uri=parent_attribute_uri,
            source_uri=source_uri,
            is_required=is_required,
        )

    def __str__(self) -> str:
        return f"NewQbAttribute('{self.label}')"

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this
