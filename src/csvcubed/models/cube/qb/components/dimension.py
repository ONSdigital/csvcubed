"""
Dimensions
----------

Represent dimensions inside an RDF Data Cube.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import pandas as pd

from csvcubed.inputs import PandasDataTypes
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.components.arbitraryrdf import (
    ArbitraryRdf,
    RdfSerialisationHint,
    TripleFragmentBase,
    validate_triple_fragment,
)
from csvcubed.models.cube.qb.components.datastructuredefinition import (
    QbColumnStructuralDefinition,
)
from csvcubed.models.cube.uristyle import URIStyle
from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.models.validatedmodel import ValidatedModel, ValidationFunction
from csvcubed.models.validationerror import ValidationError
from csvcubed.utils.validations import (
    validate_list,
    validate_optional,
    validate_str_type,
    validate_uri,
)
from csvcubed.utils.validators.uri import validate_uri as pydantic_validate_uri

from .codelist import NewQbCodeList, QbCodeList, validate_codelist


@dataclass
class QbDimension(QbColumnStructuralDefinition, ValidatedModel, ArbitraryRdf, ABC):
    @property
    @abstractmethod
    def range_uri(self) -> Optional[str]:
        pass

    @range_uri.setter
    @abstractmethod
    def range_uri(self, value: Optional[str]):
        pass

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {"range_uri": validate_optional(validate_uri)}


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

    _dimension_uri_validator = pydantic_validate_uri("dimension_uri")

    _range_uri_validator = pydantic_validate_uri("range_uri", is_optional=True)

    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        # No validation possible since we don't have the dimensions' code-list locally.
        return []

    def _get_validations(self) -> Dict[str, ValidationFunction]:

        return {
            **QbDimension._get_validations(self),
            "dimension_uri": validate_uri,
            "arbitrary_rdf": validate_list(validate_triple_fragment),
        }


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
        code_list_uri_style: Optional[URIStyle] = None,
    ) -> "NewQbDimension":
        """
        Creates a new dimension and code list from the columnar data provided.
        """
        return NewQbDimension(
            label=label,
            description=description,
            code_list=NewQbCodeList.from_data(
                CatalogMetadata(label), data, code_list_uri_style
            ),
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

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {
            **QbDimension._get_validations(self),
            "label": validate_str_type,
            "description": validate_optional(validate_str_type),
            "code_list": validate_optional(validate_codelist),
            "parent_dimension_uri": validate_optional(validate_uri),
            "source_uri": validate_optional(validate_uri),
            **UriIdentifiable._get_validations(self),
            "arbitrary_rdf": validate_list(validate_triple_fragment),
        }
