"""
SkosCodeList
------------

Contains all of the URI definitions & configuration necessary to serialise a skos:ConceptScheme.
"""
from dataclasses import dataclass

from csvcubed.models.cube import NewQbCodeList
from csvcubed.writers.urihelpers.skoscodelistconstants import SCHEMA_URI_IDENTIFIER


@dataclass
class SkosCodeListNewUriHelper:
    """
    Defines all of the URIs in a NewQbCodeList CSV-W which is serialised to disk.
    """

    code_list: NewQbCodeList

    def _get_identifier_for_document(self) -> str:
        return f"{self.code_list.metadata.uri_safe_identifier}.csv"

    def _uri_in_doc(self, identifier: str) -> str:
        """
        URIs declared in the `columns` section of the CSV-W are relative to the CSV's location.
        URIs declared in the JSON-LD metadata section of the CSV-W are relative to the metadata file's location.

        This function makes both point to the same base location - the CSV file's location. This ensures that we
        can talk about the same resources in the `columns` section and the JSON-LD metadata section.
        """
        return f"{self._get_identifier_for_document()}#{identifier}"

    def get_concept_uri(self, concept_identifier: str):
        """
        Return the URI for a concept in a new code-list
        """
        return self._uri_in_doc(concept_identifier)

    def get_scheme_uri(self):
        """
        Return the URI for the scheme
        """
        return self._uri_in_doc(SCHEMA_URI_IDENTIFIER)
