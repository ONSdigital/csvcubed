"""
Attributes
----------

Represent Attributes in an RDF Data Cube.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import pandas as pd

from csvcubed import feature_flags
from csvcubed.inputs import PandasDataTypes
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.components.codelist import NewQbCodeList, QbCodeList
from csvcubed.models.cube.qb.components.concept import NewQbConcept
from csvcubed.models.cube.qb.components.constants import ACCEPTED_DATATYPE_MAPPING
from csvcubed.models.cube.qb.components.validationerrors import (
    UndefinedAttributeValueUrisError,
)
from csvcubed.models.cube.uristyle import URIStyle
from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.models.validatedmodel import ValidationFunction
from csvcubed.models.validationerror import ValidationError
from csvcubed.utils import validations as v
from csvcubed.utils.uri import uri_safe

from .arbitraryrdf import ArbitraryRdf, RdfSerialisationHint, TripleFragmentBase
from .attributevalue import NewQbAttributeValue
from .datastructuredefinition import QbColumnStructuralDefinition


@dataclass
class QbAttribute(QbColumnStructuralDefinition, ArbitraryRdf, ABC):
    @abstractmethod
    def get_is_required(self) -> bool:
        pass

    @abstractmethod
    def get_observed_value_col_title(self) -> Optional[str]:
        pass


@dataclass
class ExistingQbAttribute(QbAttribute):
    attribute_uri: str
    is_required: bool = field(default=False, repr=False)
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)
    observed_value_col_title: Optional[str] = field(default=None, repr=False)

    def get_observed_value_col_title(self) -> Optional[str]:
        return self.observed_value_col_title

    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        return self.arbitrary_rdf

    def get_is_required(self) -> bool:
        return self.is_required

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.Component

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {RdfSerialisationHint.Component}

    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        # No validation possible since we don't have the attribute's code-list locally.
        return []

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {
            "attribute_uri": v.uri,
            "is_required": v.boolean,
            "arbitrary_rdf": v.list(v.validated_model(TripleFragmentBase)),
            "observed_value_col_title": v.optional(v.string),
        }


@dataclass
class NewQbAttribute(QbAttribute, UriIdentifiable):
    label: str
    description: Optional[str] = field(default=None, repr=False)
    code_list: Optional[QbCodeList] = field(default=None, repr=False)
    parent_attribute_uri: Optional[str] = field(default=None, repr=False)
    source_uri: Optional[str] = field(default=None, repr=False)
    is_required: bool = field(default=False, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)
    observed_value_col_title: Optional[str] = field(default=None, repr=False)

    def get_observed_value_col_title(self) -> Optional[str]:
        return self.observed_value_col_title

    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        return self.arbitrary_rdf

    def get_is_required(self) -> bool:
        return self.is_required

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
        csv_column_title: str,
        data: PandasDataTypes,
        values: Optional[List[NewQbConcept]] = None,
        description: Optional[str] = None,
        parent_attribute_uri: Optional[str] = None,
        source_uri: Optional[str] = None,
        is_required: bool = False,
        uri_safe_identifier_override: Optional[str] = None,
        arbitrary_rdf: List[TripleFragmentBase] = list(),
        observed_value_col_title: Optional[str] = None,
        code_list_uri_style: Optional[URIStyle] = None,
    ) -> "NewQbAttribute":
        if feature_flags.ATTRIBUTE_VALUE_CODELISTS:
            # If ATTRIBUTE_VALUE_CODELISTS is True, the codelist should be created from the data in the CSV via the NewQbCodelist.from_data() method
            # This will throw an error if any column cells are empty
            return NewQbAttribute(
                label=label,
                description=description,
                code_list=NewQbCodeList.from_data(
                    CatalogMetadata(label),
                    csv_column_title=csv_column_title,
                    data=data,
                    uri_style=code_list_uri_style,
                ),
                parent_attribute_uri=parent_attribute_uri,
                source_uri=source_uri,
                is_required=is_required,
                uri_safe_identifier_override=uri_safe_identifier_override,
                arbitrary_rdf=arbitrary_rdf,
                observed_value_col_title=observed_value_col_title,
            )
        else:
            # If ATTRIBUTE_VALUE_CODELISTS is False, we still need to generate a codelist, but allow for missing values by passing a list of the concepts directly to the NewQbAttribute code_list property
            return NewQbAttribute(
                label=label,
                description=description,
                code_list=NewQbCodeList(
                    metadata=CatalogMetadata(label),
                    concepts=values,  # type: ignore
                ),
                parent_attribute_uri=parent_attribute_uri,
                source_uri=source_uri,
                is_required=is_required,
                uri_safe_identifier_override=uri_safe_identifier_override,
                arbitrary_rdf=arbitrary_rdf,
                observed_value_col_title=observed_value_col_title,
            )

    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        if (
            isinstance(self.code_list, NewQbCodeList)
            and len(self.code_list.concepts) > 0
        ):
            expected_values = {concept.code for concept in self.code_list.concepts}
            actual_values = {
                uri_safe(str(v)) for v in set(data.unique()) if not pd.isna(v)
            }
            undefined_values = actual_values - expected_values
            if len(undefined_values) > 0:
                return [UndefinedAttributeValueUrisError(self, undefined_values)]
        return []

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {
            "label": v.string,
            "description": v.optional(v.string),
            "code_list": v.optional(v.validated_model(QbCodeList)),
            "parent_attribute_uri": v.optional(v.uri),
            "source_uri": v.optional(v.uri),
            "is_required": v.boolean,
            **UriIdentifiable._get_validations(self),
            "arbitrary_rdf": v.list(v.validated_model(TripleFragmentBase)),
            "observed_value_col_title": v.optional(v.string),
        }


@dataclass
class QbAttributeLiteral(QbAttribute, ABC):
    """A literal attribute allows for a non-uri-based resource to be referenced in attributes. Acceptable types
    are numeric, dates, times, and strings.
    """

    data_type: str = field(repr=False)

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {"data_type": v.any_of(v.data_type, v.uri)}


@dataclass
class ExistingQbAttributeLiteral(ExistingQbAttribute, QbAttributeLiteral):
    new_attribute_values: List[NewQbAttributeValue] = field(
        default_factory=list, init=False, repr=False
    )
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)
    observed_value_col_title: Optional[str] = field(default=None, repr=False)

    def get_observed_value_col_title(self) -> Optional[str]:
        return self.observed_value_col_title

    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        # csv-validation will check that all literals match the expected data type.
        return []

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {
            **QbAttributeLiteral._get_validations(self),
            **ExistingQbAttribute._get_validations(self),
            "new_attribute_values": v.list(v.validated_model(NewQbAttributeValue)),
            "arbitrary_rdf": v.list(v.validated_model(TripleFragmentBase)),
            "observed_value_col_title": v.optional(v.string),
        }


@dataclass
class NewQbAttributeLiteral(NewQbAttribute, QbAttributeLiteral):
    new_attribute_values: List[NewQbAttributeValue] = field(
        default_factory=list, init=False, repr=False
    )
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)
    observed_value_col_title: Optional[str] = field(default=None, repr=False)

    def get_observed_value_col_title(self) -> Optional[str]:
        return self.observed_value_col_title

    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        return self.arbitrary_rdf

    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        # csv-validation will check that all literals match the expected data type.
        return []

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {
            **QbAttributeLiteral._get_validations(self),
            **NewQbAttribute._get_validations(self),
            "new_attribute_values": v.list(v.validated_model(NewQbAttributeValue)),
            "arbitrary_rdf": v.list(v.validated_model(TripleFragmentBase)),
            "observed_value_col_title": v.optional(v.string),
        }
