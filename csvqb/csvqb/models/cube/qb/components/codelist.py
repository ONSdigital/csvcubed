from typing import Set, Optional, List
from abc import ABC
import pandas as pd


from .datastructuredefinition import QbDataStructureDefinition
from csvqb.models.validationerror import ValidationError
from csvqb.utils.uri import uri_safe


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

    def __init__(self, code: str, label: str, parent_code: Optional[str] = None):
        self.code: str = code
        self.label: str = label
        self.parent_code: Optional[str] = parent_code

    def __str__(self) -> str:
        return f"NewQbConcept('{self.code}', '{self.label}')"

    def __hash__(self):
        return self.code.__hash__()


class NewQbCodeList(QbCodeList):
    """
    Contains the metadata necessary to create a new skos:ConceptScheme which is local to a dataset.
    """

    def __init__(self,
                 label: str,
                 concepts: List[NewQbConcept],
                 uri_safe_identifier: Optional[str] = None,
                 description: Optional[str] = None,
                 variant_of_uris: List[str] = [],
                 source_uri: Optional[str] = None):
        self.label: str = label
        self.concepts: List[NewQbConcept] = concepts
        self.uri_safe_identifier: str = uri_safe(label) if uri_safe_identifier is None else uri_safe_identifier
        self.description: Optional[str] = description
        self.variant_of_uris: List[str] = variant_of_uris  # For xkos:variant usage.
        self.source_uri: Optional[str] = source_uri

    def __str__(self) -> str:
        return f"NewQbCodeList('{self.label}')"

    @staticmethod
    def from_data(label: str,
                  data: pd.Series,
                  uri_safe_identifier: Optional[str] = None,
                  description: Optional[str] = None,
                  variant_of_uris: List[str] = [],
                  source_uri: Optional[str] = None) -> "NewQbCodeList":

        concepts = [NewQbConcept(uri_safe(c), c) for c in sorted(set(data))]
        return NewQbCodeList(label,
                             concepts,
                             uri_safe_identifier=uri_safe_identifier,
                             description=description,
                             variant_of_uris=variant_of_uris,
                             source_uri=source_uri)

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this.

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this.
