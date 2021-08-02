"""
Code Lists
----------
"""
from dataclasses import dataclass, field
from typing import Optional, List
from abc import ABC

from csvqb.models.uriidentifiable import UriIdentifiable
from .datastructuredefinition import QbDataStructureDefinition
from csvqb.models.cube.csvqb.catalog import CatalogMetadata
from csvqb.models.validationerror import ValidationError
from csvqb.utils.uri import uri_safe
from csvqb.inputs import PandasDataTypes, pandas_input_to_columnar_str


@dataclass
class QbCodeList(QbDataStructureDefinition, ABC):
    pass


@dataclass
class ExistingQbCodeList(QbCodeList):
    """
    Contains metadata necessary to link a dimension to an existing skos:ConceptScheme.
    """
    concept_scheme_uri: str

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # TODO: implement this.


@dataclass(eq=False, unsafe_hash=False)
class NewQbConcept(UriIdentifiable):
    label: str
    code: str = field(default="")
    parent_code: Optional[str] = field(default=None, repr=False)
    sort_order: Optional[int] = field(default=None, repr=False)
    description: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)

    def get_identifier(self) -> str:
        return self.code

    def __post_init__(self):
        if self.code.strip() == "":
            self.code = uri_safe(self.label)

    def __eq__(self, other):
        return isinstance(other, NewQbConcept) and self.code == other.code

    def __hash__(self):
        return self.code.__hash__()


@dataclass
class NewQbCodeList(QbCodeList):
    """
    Contains the metadata necessary to create a new skos:ConceptScheme which is local to a dataset.
    """
    metadata: CatalogMetadata
    concepts: List[NewQbConcept]
    variant_of_uris: List[str] = field(default_factory=list)

    @staticmethod
    def from_data(
        metadata: CatalogMetadata,
        data: PandasDataTypes,
        variant_of_uris: List[str] = [],
    ) -> "NewQbCodeList":
        columnar_data = pandas_input_to_columnar_str(data)
        concepts = [NewQbConcept(c) for c in sorted(set(columnar_data))]
        return NewQbCodeList(metadata, concepts, variant_of_uris=variant_of_uris)

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # TODO: implement this.
