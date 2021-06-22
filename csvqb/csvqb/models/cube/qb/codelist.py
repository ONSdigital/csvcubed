from typing import Set, Optional
from abc import ABC, abstractmethod


class QbCodeList(ABC):

    @abstractmethod
    def validate(self, code_to_ensure_exist: Set[str]) -> bool:
        """
        Validates a CodeList and ensures that the given codes are defined within.
        :param code_to_ensure_exist:
        :return:
        """
        pass


class ExistingQbCodeList(QbCodeList):
    """
    Contains metadata necessary to link a dimension to an existing skos:ConceptScheme.
    """
    concept_scheme_uri: str

    def __init__(self, concept_scheme_uri: str):
        self.concept_scheme_uri = concept_scheme_uri

    def validate(self, code_to_ensure_exist: Set[str]) -> bool:
        """
        TODO: Probably want to fetch the existing concept scheme from PMD (and verify that it exists).
        We should then check that all of the values in `data` are defined in the concept scheme, if not,
        raise some warnings.
        :param code_to_ensure_exist:
        :return:
        """
        raise Exception("Not implemented yet.")


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

    def validate(self, code_to_ensure_exist: Set[str]) -> bool:
        """
        TODO: Seems sensible to check that all of the values live within the concept scheme we're defining locally.
        TODO: Ensure all of the other metadata is correctly configured
        :return:
        """
        raise Exception("Not implemented yet.")
