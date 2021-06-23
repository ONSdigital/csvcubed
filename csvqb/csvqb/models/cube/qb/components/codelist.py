from typing import Set, Optional, List
from abc import ABC, abstractmethod

import pandas as pd

from .datastructuredefinition import QbDataStructureDefinition
from csvqb.models.validationerror import ValidationError


class QbCodeList(QbDataStructureDefinition, ABC):
    pass


class ExistingQbCodeList(QbCodeList):
    """
    Contains metadata necessary to link a dimension to an existing skos:ConceptScheme.
    """
    concept_scheme_uri: str

    def __init__(self, concept_scheme_uri: str):
        self.concept_scheme_uri = concept_scheme_uri

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this.

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this.


class NewQbConcept:
    code: str
    label: str
    parent_code: Optional[str]

    def __init__(self, code: str, label: str, parent_code: Optional[str] = None):
        self.code = code
        self.label = label
        self.parent_code = parent_code

    def __hash__(self):
        return self.code.__hash__()


class NewQbCodeList(QbCodeList):
    """
    Contains the metadata necessary to create a new skos:ConceptScheme which is local to a dataset.
    """
    concepts: Set[NewQbConcept]

    def __init__(self, concepts: Set[NewQbConcept]):
        self.concepts = concepts

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this.

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this.
