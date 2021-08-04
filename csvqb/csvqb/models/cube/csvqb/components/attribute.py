"""
Attributes
----------
"""
from dataclasses import dataclass, field
from typing import Optional, List
from abc import ABC, abstractmethod

from csvqb.models.uriidentifiable import UriIdentifiable
from .datastructuredefinition import ColumnarQbDataStructureDefinition
from .codelist import QbCodeList, NewQbCodeList
from csvqb.models.validationerror import ValidationError
from csvqb.inputs import PandasDataTypes
from csvqb.models.cube.csvqb.catalog import CatalogMetadata


@dataclass
class QbAttribute(ColumnarQbDataStructureDefinition, ABC):
    @abstractmethod
    def is_required(self) -> bool:
        pass


@dataclass
class ExistingQbAttribute(QbAttribute):
    attribute_uri: str
    is_required: bool = field(default=False, repr=False)

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # TODO: implement this


@dataclass
class NewQbAttribute(QbAttribute, UriIdentifiable):
    label: str
    description: Optional[str] = field(default=None, repr=False)
    code_list: Optional[QbCodeList] = field(default=None, repr=False)
    parent_attribute_uri: Optional[str] = field(default=None, repr=False)
    source_uri: Optional[str] = field(default=None, repr=False)
    is_required: bool = field(default=False, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)

    def get_identifier(self) -> str:
        return self.label

    @staticmethod
    def from_data(
        label: str,
        data: PandasDataTypes,
        description: Optional[str] = None,
        parent_attribute_uri: Optional[str] = None,
        source_uri: Optional[str] = None,
        is_required: bool = False,
        uri_safe_identifier_override: Optional[str] = None,
    ):
        return NewQbAttribute(
            label,
            description=description,
            code_list=NewQbCodeList.from_data(CatalogMetadata(label), data),
            parent_attribute_uri=parent_attribute_uri,
            source_uri=source_uri,
            is_required=is_required,
            uri_safe_identifier_override=uri_safe_identifier_override,
        )

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # TODO: implement this
