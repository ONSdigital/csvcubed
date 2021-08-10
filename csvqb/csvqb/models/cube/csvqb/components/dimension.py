"""
Dimensions
----------
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set
from abc import ABC, abstractmethod

import pandas as pd

from csvqb.models.uriidentifiable import UriIdentifiable
from .arbitraryrdf import ArbitraryRdf, RdfSerialisationHint, TripleFragmentBase
from .datastructuredefinition import ColumnarQbDataStructureDefinition
from .codelist import QbCodeList, NewQbCodeList
from csvqb.models.validationerror import ValidationError
from csvqb.inputs import PandasDataTypes, pandas_input_to_columnar_list
from ..catalog import CatalogMetadata


@dataclass
class QbDimension(ColumnarQbDataStructureDefinition, ArbitraryRdf, ABC):
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
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {RdfSerialisationHint.Component}

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.Component

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # TODO: add more validation checks


@dataclass
class NewQbDimension(QbDimension, UriIdentifiable):
    label: str
    description: Optional[str] = field(default=None, repr=False)
    code_list: Optional[QbCodeList] = field(default=None, repr=False)
    parent_dimension_uri: Optional[str] = field(default=None, repr=False)
    source_uri: Optional[str] = field(default=None, repr=False)
    range_uri: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    @staticmethod
    def from_data(
        label: str,
        data: PandasDataTypes,
        description: Optional[str] = None,
        parent_dimension_uri: Optional[str] = None,
        source_uri: Optional[str] = None,
        range_uri: Optional[str] = None,
        uri_safe_identifier_override: Optional[str] = None,
        arbitrary_rdf: List[TripleFragmentBase] = [],
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
            arbitrary_rdf=arbitrary_rdf,
        )

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {RdfSerialisationHint.Component, RdfSerialisationHint.Property}

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.Property

    def get_identifier(self) -> str:
        return self.label

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        # todo: Add more validation checks
        errors = []

        colmnar_data = pandas_input_to_columnar_list(data)
        colmnar_data

        if self.code_list is not None:
            errors += self.code_list.validate_data(data)

        return errors
