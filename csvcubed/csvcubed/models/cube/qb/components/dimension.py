"""
Dimensions
----------

Represent dimensions inside an RDF Data Cube.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set
from abc import ABC, abstractmethod
import pandas as pd

from csvcubed.inputs import PandasDataTypes
from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.models.cube.qb.components.arbitraryrdf import (
    ArbitraryRdf,
    RdfSerialisationHint,
    TripleFragmentBase,
)
from csvcubed.models.cube.qb.components.datastructuredefinition import (
    QbColumnStructuralDefinition,
)
from .codelist import (
    QbCodeList,
    NewQbCodeList,
)
from csvcubed.models.validationerror import ValidationError
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.utils.validators.uri import validate_uri


@dataclass
class QbDimension(QbColumnStructuralDefinition, ArbitraryRdf, ABC):
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

    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        return self.arbitrary_rdf

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {RdfSerialisationHint.Component}

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.Component

    _dimension_uri_validator = validate_uri("dimension_uri")

    _range_uri_validator = validate_uri("range_uri", is_optional=True)

    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        # No validation possible since we don't have the dimensions' code-list locally.
        return []


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

    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        return self.arbitrary_rdf

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
            label=label,
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

    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        # Leave csv-lint to do the validation here. It will enforce Foreign Key constraints on code lists.
        if isinstance(self.code_list, NewQbCodeList):
            return self.code_list.validate_data(data, column_csv_title)

        return []
