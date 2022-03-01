"""
Inspect SPARQL query results
----------------------------
"""

from os import linesep
from dataclasses import dataclass, field
from typing import List

from rdflib.query import ResultRow

from csvcubed.utils.sparql import none_or_map


@dataclass()
class CatalogMetadataSparqlResult:
    """
    TODO: Add description here
    """

    sparql_result: ResultRow

    def _get_printable_list_str(self, items: List) -> str:
        """
        TODO: Add description here

        Member of :file:`./models/inspectsparqlresults`.

        :return: `str` - string representation of the list
        """
        if len(items) == 0 or len(items[0]) == 0:
            return "None"

        output_str = ""
        for item in items:
            output_str = f"{output_str}{linesep}\t\t-- {item}"
        return output_str

    def get_formatted_str(self) -> str:
        formatted_landing_pages = self._get_printable_list_str(self.landing_pages)
        formatted_themes = self._get_printable_list_str(self.themes)
        formatted_keywords = self._get_printable_list_str(self.keywords)
        return f"{linesep}\t- Title: {self.title}{linesep}\t- Label: {self.label}{linesep}\t- Issued: {self.issued}{linesep}\t- Modified: {self.modified}{linesep}\t- License: {self.license}{linesep}\t- Creator: {self.creator}{linesep}\t- Publisher: {self.publisher}{linesep}\t- Landing Pages: {formatted_landing_pages}{linesep}\t- Themes: {formatted_themes}{linesep}\t- Keywords: {formatted_keywords}{linesep}\t- Contact Point: {self.contact_point}{linesep}\t- Identifier: {self.identifier}{linesep}\t- Comment: {self.comment}{linesep}\t- Description: {self.description}{linesep}\t"

    def __post_init__(self):
        result_dict = self.sparql_result.asdict()

        self.title: str = result_dict["title"]
        self.label: str = result_dict["label"]
        self.issued: str = result_dict["issued"]
        self.modified: str = result_dict["modified"]
        self.license: str = none_or_map(result_dict.get("license"), str)
        self.creator: str = none_or_map(result_dict.get("creator"), str)
        self.publisher: str = none_or_map(result_dict.get("publisher"), str)
        self.landing_pages: list[str] = str(result_dict["landingPages"]).split("|")
        self.themes: list[str] = str(result_dict["themes"]).split("|")
        self.keywords: list[str] = str(result_dict["keywords"]).split("|")
        self.contact_point: str = none_or_map(result_dict.get("contact_point"), str)
        self.identifier: str = result_dict["identifier"]
        self.comment: str = none_or_map(result_dict.get("comment"), str)
        self.description: str = str(
            none_or_map(result_dict.get("description"), str)
        ).replace(linesep, f"{linesep}\t\t")
