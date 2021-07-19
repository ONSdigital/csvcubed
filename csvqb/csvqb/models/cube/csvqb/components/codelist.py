from typing import Optional, List
from abc import ABC
import pandas as pd


from .datastructuredefinition import QbDataStructureDefinition
from csvqb.models.cube.csvqb.catalog import CatalogMetadata
from csvqb.models.validationerror import ValidationError
from csvqb.utils.uri import uri_safe
from csvqb.inputs import PandasDataTypes, pandas_input_to_columnar_str


class QbCodeList(QbDataStructureDefinition, ABC):
    pass


class ExistingQbCodeList(QbCodeList):
    """
    Contains metadata necessary to link a dimension to an existing skos:ConceptScheme.
    """

    def __init__(self, concept_scheme_uri: str):
        self.concept_scheme_uri: str = concept_scheme_uri

    def __str__(self) -> str:
        return f"ExistingQbCodeList('{self.concept_scheme_uri}')"

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this.

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this.


class NewQbConcept:

    def __init__(self,
                 label: str,
                 code: Optional[str] = None,
                 parent_code: Optional[str] = None,
                 sort_order: Optional[int] = None,
                 description: Optional[str] = None):
        self.label: str = label
        self.code: str = code or uri_safe(label)
        self.parent_code: Optional[str] = parent_code
        self.sort_order: Optional[int] = sort_order
        self.description: Optional[str] = description

    def __str__(self) -> str:
        return f"NewQbConcept('{self.code}', '{self.label}')"

    def __hash__(self):
        return self.code.__hash__()


class NewQbCodeList(QbCodeList):
    """
    Contains the metadata necessary to create a new skos:ConceptScheme which is local to a dataset.
    """

    def __init__(self,
                 metadata: CatalogMetadata,
                 concepts: List[NewQbConcept],
                 variant_of_uris: List[str] = []):
        self.metadata: CatalogMetadata = metadata
        self.concepts: List[NewQbConcept] = concepts
        self.variant_of_uris: List[str] = variant_of_uris  # For xkos:variant usage.

    def __str__(self) -> str:
        return f"NewQbCodeList('{self.metadata.title}')"

    @staticmethod
    def from_data(metadata: CatalogMetadata,
                  data: PandasDataTypes,
                  variant_of_uris: List[str] = []) -> "NewQbCodeList":
        columnar_data = pandas_input_to_columnar_str(data)
        concepts = [NewQbConcept(c) for c in sorted(set(columnar_data))]
        return NewQbCodeList(metadata,
                             concepts,
                             variant_of_uris=variant_of_uris)

    def validate(self) -> List[ValidationError]:
        return self.metadata.validate() \
               + []  # TODO: augment this.

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this.
