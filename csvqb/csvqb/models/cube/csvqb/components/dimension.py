"""
Dimensions
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
from ..catalog import CatalogMetadata


@dataclass
class QbDimension(ColumnarQbDataStructureDefinition, ABC):
    @property
    @abstractmethod
    def range_uri(self) -> Optional[str]:
        pass

    @range_uri.setter
    @abstractmethod
    def range_uri(self, value: Optional[str]):
        pass


@dataclass
class ExistingQbDimension(QbDimension):
    dimension_uri: str
    range_uri: Optional[str] = field(default=None, repr=False)

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # TODO: add more validation checks


@dataclass
class NewQbDimension(QbDimension, UriIdentifiable):
    label: str
    description: Optional[str] = field(default=None, repr=False)
    # todo: Ensure we link the code-list to the qb column component somehow
    code_list: Optional[QbCodeList] = field(default=None, repr=False)
    parent_dimension_uri: Optional[str] = field(default=None, repr=False)
    source_uri: Optional[str] = field(default=None, repr=False)
    range_uri: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)

    def get_identifier(self) -> str:
        return self.label

    @staticmethod
    def from_data(
        label: str,
        data: PandasDataTypes,
        description: Optional[str] = None,
        parent_dimension_uri: Optional[str] = None,
        source_uri: Optional[str] = None,
        range_uri: Optional[str] = None,
        uri_safe_identifier_override: Optional[str] = None,
    ) -> "NewQbDimension":
        """
        Creates a new dimension and code list from the columnar data provided.
        """
        return NewQbDimension(
            label,
            description=description,
            code_list=NewQbCodeList.from_data(CatalogMetadata(label), data),
            parent_dimension_uri=parent_dimension_uri,
            source_uri=source_uri,
            range_uri=range_uri,
            uri_safe_identifier_override=uri_safe_identifier_override,
        )

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        # todo: Add more validation checks
        if self.code_list is not None:
            return self.code_list.validate_data(data)

        return []
