"""
Attributes
----------
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set
from abc import ABC, abstractmethod
from pydantic import validator
import pandas as pd

from csvqb.models.uriidentifiable import UriIdentifiable
from .arbitraryrdf import (
    ArbitraryRdf,
    TripleFragmentBase,
    RdfSerialisationHint,
)
from .datastructuredefinition import ColumnarQbDataStructureDefinition
from csvqb.models.validationerror import ValidationError
from .validationerrors import UndefinedValuesError
from csvqb.inputs import PandasDataTypes, pandas_input_to_columnar_optional_str

from csvqb.utils.uri import uri_safe
from csvqb.utils.validators.uri import validate_uri


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
        if len(self.new_attribute_values) > 0:  # type: ignore
            expected_values = {
                av.uri_safe_identifier for av in self.new_attribute_values  # type: ignore
            }
            actual_values = {
                uri_safe(v)
                for v in set(data.unique().astype(object).flatten())
                if not pd.isna(v)
            }
            undefined_values = expected_values - actual_values

            if len(undefined_values) > 0:
                return [
                    UndefinedValuesError(
                        self, "new attribute value URI", undefined_values
                    )
                ]

        return []


accepted_data_types = {
    "anyURI",
    "boolean",
    "date",
    "dateTime",
    "dateTimeStamp",
    "decimal",
    "integer",
    "long",
    "int",
    "short",
    "nonNegativeInteger",
    "positiveInteger",
    "unsignedLong",
    "unsignedInt",
    "unsignedShort",
    "nonPositiveInteger",
    "negativeInteger",
    "double",
    "float",
    "string",
    "language",
    "time",
}


@dataclass
class QbAttributeLiteral(QbAttribute, ABC):
    """A literal attribute allows for a non-uri-based resource to be referenced in attributes. Acceptable types
    are numeric, dates, times, and strings.
    """

    data_type: str = field(repr=False)

    @validator("data_type", pre=True, always=True)
    def data_type_value(cls, data_type):
        if data_type not in accepted_data_types:
            raise ValueError(f"Literal type '{data_type}' not supported")
        return data_type or "string"


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

    _attribute_uri_validator = validate_uri("attribute_uri")

    def validate_data(
        self, data: pd.Series, column_csvw_name: str, csv_column_uri_template: str
    ) -> List[ValidationError]:
        return self._validate_data_new_attribute_values(data)


@dataclass
class ExistingQbAttributeLiteral(ExistingQbAttribute, QbAttributeLiteral):
    new_attribute_values: List[NewQbAttributeValue] = field(
        default_factory=list, init=False, repr=False
    )
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    def validate_data(
        self, data: pd.Series, column_csvw_name: str, csv_column_uri_template: str
    ) -> List[ValidationError]:
        # csv-validation will check that all literals match the expected data type.
        return []


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
        columnar_data = pandas_input_to_columnar_optional_str(data)
        new_attribute_values_from_column = [
            NewQbAttributeValue(v)
            for v in sorted(set([d for d in columnar_data if d is not None]))
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
        self, data: pd.Series, column_csvw_name: str, csv_column_uri_template: str
    ) -> List[ValidationError]:
        return self._validate_data_new_attribute_values(data)


@dataclass
class NewQbAttributeLiteral(NewQbAttribute, QbAttributeLiteral):
    new_attribute_values: List[NewQbAttributeValue] = field(
        default_factory=list, init=False, repr=False
    )
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    def validate_data(
        self, data: pd.Series, column_csvw_name: str, csv_column_uri_template: str
    ) -> List[ValidationError]:
        # csv-validation will check that all literals match the expected data type.
        return []
