"""
Inspect SPARQL query results
----------------------------
"""

from os import linesep
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
from csvcubed.utils.qb.components import get_printable_component_property
from rdflib import URIRef

from rdflib.query import ResultRow

from csvcubed.utils.sparql import none_or_map
from csvcubed.utils.printable import (
    get_printable_list_str,
    get_printable_tabular_list_str,
    get_printable_tabular_str,
)


@dataclass()
class CatalogMetadataSparqlResult:
    """
    Model to represent result of the `select_csvw_catalog_metadata` sparql query.
    """

    sparql_result: ResultRow

    @property
    def output_str(self) -> str:
        formatted_landing_pages: str = get_printable_list_str(self.landing_pages)
        formatted_themes: str = get_printable_list_str(self.themes)
        formatted_keywords: str = get_printable_list_str(self.keywords)
        formatted_description: str = (
            self.description.replace(linesep, f"{linesep}\t\t")
            if self.description != ""
            else "None"
        )
        return f"{linesep}\t- Title: {self.title}{linesep}\t- Label: {self.label}{linesep}\t- Issued: {self.issued}{linesep}\t- Modified: {self.modified}{linesep}\t- License: {self.license}{linesep}\t- Creator: {self.creator}{linesep}\t- Publisher: {self.publisher}{linesep}\t- Landing Pages: {formatted_landing_pages}{linesep}\t- Themes: {formatted_themes}{linesep}\t- Keywords: {formatted_keywords}{linesep}\t- Contact Point: {self.contact_point}{linesep}\t- Identifier: {self.identifier}{linesep}\t- Comment: {self.comment}{linesep}\t- Description: {formatted_description}"

    def __post_init__(self):
        result_dict = self.sparql_result.asdict()

        self.title: str = str(result_dict["title"])
        self.label: str = str(result_dict["label"])
        self.issued: str = str(result_dict["issued"])
        self.modified: str = str(result_dict["modified"])
        self.license: str = none_or_map(result_dict.get("license"), str)
        self.creator: str = none_or_map(result_dict.get("creator"), str)
        self.publisher: str = none_or_map(result_dict.get("publisher"), str)
        self.landing_pages: list[str] = str(result_dict["landingPages"]).split("|")
        self.themes: list[str] = str(result_dict["themes"]).split("|")
        self.keywords: list[str] = str(result_dict["keywords"]).split("|")
        self.contact_point: str = none_or_map(result_dict.get("contact_point"), str)
        self.identifier: str = str(result_dict["identifier"])
        self.comment: str = none_or_map(result_dict.get("comment"), str)
        self.description: str = none_or_map(result_dict.get("description"), str) or ""


@dataclass()
class DSDLabelURISparqlResult:
    """
    Model to represent result of the `select_csvw_dsd_dataset_label_and_dsd_def_uri` sparql query.
    """

    sparql_result: ResultRow

    @property
    def output_str(self) -> str:
        return f"{linesep}\t- Dataset Label: {self.dataset_label}"

    def __post_init__(self):
        result_dict = self.sparql_result.asdict()

        self.dataset_label: str = result_dict["dataSetLabel"]
        self.dsd_uri: URIRef = result_dict["dataStructureDefinition"]


@dataclass()
class QubeComponent:
    """
    Model to represent the result of an individual component.
    """

    result: ResultRow
    json_path: Path

    def to_dict(self) -> Dict:
        return {
            "Property": self.property,
            "Property Label": self.property_label,
            "Property Type": self.property_type,
            "Column Title": self.csv_col_title,
            "Required": self.required,
        }

    def __post_init__(self):
        self.property = get_printable_component_property(
            self.json_path, self.result["componentProperty"]
        )
        self.property_label = (
            none_or_map(self.result.get("componentPropertyLabel"), str) or ""
        )
        self.property_type = (
            none_or_map(self.result.get("componentPropertyType"), str) or ""
        )
        self.csv_col_title = none_or_map(self.result.get("csvColumnTitle"), str) or ""
        self.required = none_or_map(self.result.get("required"), str)


@dataclass()
class QubeComponentsSparqlResult:
    """
    Model to represent result of the `select_csvw_dsd_qube_components` sparql query.
    """

    sparql_results: List[ResultRow]
    json_path: Path

    @property
    def output_str(self) -> str:
        formatted_components = get_printable_tabular_str(
            [component.to_dict() for component in self.qube_components]
        )
        return f"{linesep}\t- Number of Components: {self.num_components}{linesep}\t- Components:{linesep}{formatted_components}"

    def __post_init__(self):
        self.qube_components: List[QubeComponent] = list(
            map(
                lambda result: QubeComponent(result, self.json_path),
                self.sparql_results,
            )
        )
        self.num_components: int = len(self.qube_components)


@dataclass()
class ColsWithSupressOutputTrueSparlqlResult:
    """
    Model to represent result of the `select_cols_where_supress_output_is_true` sparql query.
    """

    sparql_results: List[ResultRow]

    @property
    def output_str(self) -> str:
        return f"{linesep}- Columns where suppress output is true: {get_printable_list_str(self.columns)}"

    def __post_init__(self):
        self.columns = list(
            map(
                lambda result: str(result["csvColumnTitle"]),
                self.sparql_results,
            )
        )


@dataclass()
class Codelist:
    """
    Model to represent the result of an individual codelist.
    """

    result: ResultRow
    json_path: Path

    def to_dict(self) -> Dict:
        return {
            "Code List": self.codeList,
            "Code List Label": self.codeListLabel,
            "Columns Used In": self.colsInUsed,
        }

    def __post_init__(self):
        self.codeList = get_printable_component_property(
            self.json_path, self.result["codeList"]
        )
        self.codeListLabel = none_or_map(self.result.get("codeListLabel"), str) or ""
        self.colsInUsed = get_printable_tabular_list_str(
            str(self.result["csvColumnsUsedIn"]).split("|")
        )


@dataclass()
class CodelistInfoSparqlResult:
    """
    Model to represent result of the `select_dsd_code_list_and_cols` sparql query.
    """

    sparql_results: List[ResultRow]
    json_path: Path

    @property
    def output_str(self) -> str:
        formatted_codelists = get_printable_tabular_str(
            [codelist.to_dict() for codelist in self.codelists]
        )
        return f"{linesep}\t- Number of Code Lists: {self.num_codelists}{linesep}\t- Code Lists:{linesep}{formatted_codelists}"

    def __post_init__(self):
        self.codelists: List[Codelist] = list(
            map(
                lambda result: Codelist(result, self.json_path),
                self.sparql_results,
            )
        )
        self.num_codelists: int = len(self.codelists)
