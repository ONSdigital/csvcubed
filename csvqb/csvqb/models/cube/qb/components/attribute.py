"""
Attributes
----------
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set
from abc import ABC, abstractmethod
import pandas as pd

from csvqb.models.uriidentifiable import UriIdentifiable
from .arbitraryrdf import (
    ArbitraryRdf,
    TripleFragmentBase,
    RdfSerialisationHint,
)
from .datastructuredefinition import ColumnarQbDataStructureDefinition
from csvqb.models.validationerror import ValidationError
from csvqb.inputs import PandasDataTypes, pandas_input_to_columnar_str
from .validationerrors import UndefinedValuesError


@dataclass
class NewQbAttributeValue(UriIdentifiable, ArbitraryRdf):
    label: str
    description: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)
    source_uri: Optional[str] = field(default=None, repr=False)
    parent_attribute_value_uri: Optional[str] = field(default=None, repr=False)
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.AttributeValue

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {RdfSerialisationHint.AttributeValue}

    def get_identifier(self) -> str:
        return self.label


@dataclass
class QbAttribute(ColumnarQbDataStructureDefinition, ArbitraryRdf, ABC):
    @abstractmethod
    def is_required(self) -> bool:
        pass

    @abstractmethod
    def new_attribute_values(self) -> List[NewQbAttributeValue]:
        pass

    def _validate_data_new_attribute_values(
        self, data: pd.Series
    ) -> List[ValidationError]:
        """
        Validate that all of the values in :obj`data` are defined in :attr:`new_attribute_values` if values are defined.
        """
        if len(self.new_attribute_values) > 0:
            expected_values = {
                av.uri_safe_identifier for av in self.new_attribute_values
            }
            actual_values = set(data.unique().flatten())
            undefined_values = expected_values - actual_values

            if len(undefined_values) > 0:
                return [UndefinedValuesError(self, undefined_values)]

        return []


@dataclass
class ExistingQbAttribute(QbAttribute):
    attribute_uri: str
    new_attribute_values: List[NewQbAttributeValue] = field(
        default_factory=list, repr=False
    )
    is_required: bool = field(default=False, repr=False)
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.Component

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {RdfSerialisationHint.Component}

    def validate_data(
        self, data: pd.Series, column_csvw_name: str, output_uri_template: str
    ) -> List[ValidationError]:
        return self._validate_data_new_attribute_values(data)


@dataclass
class NewQbAttribute(QbAttribute, UriIdentifiable):
    label: str
    description: Optional[str] = field(default=None, repr=False)
    new_attribute_values: List[NewQbAttributeValue] = field(
        default_factory=list, repr=False
    )
    parent_attribute_uri: Optional[str] = field(default=None, repr=False)
    source_uri: Optional[str] = field(default=None, repr=False)
    is_required: bool = field(default=False, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.Property

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {
            RdfSerialisationHint.Property,
            RdfSerialisationHint.Component,
        }

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
        arbitrary_rdf: List[TripleFragmentBase] = list(),
    ) -> "NewQbAttribute":
        columnar_data = pandas_input_to_columnar_str(data)
        new_attribute_values_from_column = [
            NewQbAttributeValue(v) for v in sorted(set(columnar_data))
        ]

        return NewQbAttribute(
            label,
            description=description,
            new_attribute_values=new_attribute_values_from_column,
            parent_attribute_uri=parent_attribute_uri,
            source_uri=source_uri,
            is_required=is_required,
            uri_safe_identifier_override=uri_safe_identifier_override,
            arbitrary_rdf=arbitrary_rdf,
        )

    def validate_data(
        self, data: pd.Series, column_csvw_name: str, output_uri_template: str
    ) -> List[ValidationError]:
        return self._validate_data_new_attribute_values(data)
