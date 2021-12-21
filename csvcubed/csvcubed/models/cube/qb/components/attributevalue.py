"""
Attributes
----------
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set

from csvcubed.models.uriidentifiable import UriIdentifiable
from .arbitraryrdf import (
    ArbitraryRdf,
    TripleFragmentBase,
    RdfSerialisationHint,
)
from .datastructuredefinition import SecondaryQbStructuralDefinition


@dataclass
class NewQbAttributeValue(
    SecondaryQbStructuralDefinition, UriIdentifiable, ArbitraryRdf
):
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
