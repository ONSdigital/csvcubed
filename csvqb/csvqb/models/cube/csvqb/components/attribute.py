"""
Attributes
----------
"""
from dataclasses import dataclass, field
from typing import Optional, List
from abc import ABC, abstractmethod

from csvqb.models.uriidentifiable import UriIdentifiable
from sharedmodels.rdf.namespaces import QB
from .datastructuredefinition import ColumnarQbDataStructureDefinition
from csvqb.models.validationerror import ValidationError, UnsupportedDataTypeError
from csvqb.inputs import PandasDataTypes, pandas_input_to_columnar_str


@dataclass
class NewQbAttributeValue(UriIdentifiable):
    label: str
    description: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)
    source_uri: Optional[str] = field(default=None, repr=False)
    parent_attribute_value_uri: Optional[str] = field(default=None, repr=False)

    def get_identifier(self) -> str:
        return self.label

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # TODO: implement this


@dataclass
class QbAttribute(ColumnarQbDataStructureDefinition, ABC):
    @abstractmethod
    def is_required(self) -> bool:
        pass

    @abstractmethod
    def new_attribute_values(self) -> List[NewQbAttributeValue]:
        pass


@dataclass
class QbAttributeLiteral(QbAttribute, ABC):
    data_type: str = field(repr=False)

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        accepted_data_types =  ["anyURI", "boolean", "date", "dateTime", "dateTimeStamp", "decimal", "integer", "long",
                                "int", "short", "nonNegativeInteger", "positiveInteger", "unsignedLong", "unsignedInt",
                                "unsignedShort","nonPositiveInteger", "negativeInteger", "double", "float", "string", 
                                "language", "time"]

        errors = []

        if self.data_type not in accepted_data_types:
            errors += [UnsupportedDataTypeError()]
        
        return errors

@dataclass
class ExistingQbAttribute(QbAttribute):
    attribute_uri: str
    new_attribute_values: List[NewQbAttributeValue] = field(
        default_factory=list, repr=False
    )
    is_required: bool = field(default=False, repr=False)

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # TODO: implement this


@dataclass
class ExistingQbAttributeLiteral(ExistingQbAttribute, QbAttributeLiteral):

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        errors = []

        errors.append(*[ExistingQbAttribute.validate_data(self, data)])

        return errors
    

@dataclass
class NewQbAttribute(QbAttribute, UriIdentifiable):
    label: str  # NewQbAttribute(label="Whatever you label is")
    description: Optional[str] = field(default=None, repr=False)
    new_attribute_values: List[NewQbAttributeValue] = field(
        default_factory=list, repr=False
    )
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
        )

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # TODO: implement this


@dataclass
class NewQbAttributeLiteral(NewQbAttribute, QbAttributeLiteral):
    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        errors = []

        errors.append(*[NewQbAttribute.validate_data(self, data)])

        return errors
