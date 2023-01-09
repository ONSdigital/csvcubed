"""
SkosCodeList
------------

Contains all of the URI definitions & configuration necessary to serialise a skos:ConceptScheme.
"""
from dataclasses import dataclass

from csvcubed.models.cube.qb.components.codelist import NewQbCodeList
from csvcubed.models.cube.uristyle import URIStyle

from .constants import SCHEMA_URI_IDENTIFIER


@dataclass
class NewResourceUriGenerator:
    """
    Defines all of the URIs in a Code List CSV-W which is serialised to disk.
    """

    code_list: NewQbCodeList
    default_uri_style: URIStyle

    def _get_identifier_for_document(self) -> str:
        identifier = self.code_list.metadata.uri_safe_identifier

        resolved_uri_style = self._resolve_uri_style()
        if resolved_uri_style == URIStyle.Standard:
            return identifier + ".csv"
        elif resolved_uri_style == URIStyle.WithoutFileExtensions:
            return identifier
        else:
            raise ValueError(f"Unhandled URI Style '{self.code_list.uri_style}'.")

    def _resolve_uri_style(self) -> URIStyle:
        if self.code_list and self.code_list.uri_style:
            return self.code_list.uri_style
        else:
            return self.default_uri_style

    def _uri_in_doc(self, identifier: str) -> str:
        """
        URIs declared in the `columns` section of the CSV-W are relative to the CSV's location.
        URIs declared in the JSON-LD metadata section of the CSV-W are relative to the metadata file's location.

        This function makes both point to the same base location - the CSV file's location. This ensures that we
        can talk about the same resources in the `columns` section and the JSON-LD metadata section.
        """
        return f"{self._get_identifier_for_document()}#{identifier}"

    def get_uri_prefix_for_doc(self):
        """
        Return the prefix for all new URIs defined in the document.
        """
        return self._uri_in_doc("")

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

    def get_activity_uri(self) -> str:
        """
        Return the URI for the build activity
        """
        return self._uri_in_doc("csvcubed-build-activity")
