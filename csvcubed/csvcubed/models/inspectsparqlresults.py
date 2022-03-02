"""
Inspect SPARQL query results
----------------------------
"""

from dataclasses import dataclass
from os import linesep
from pathlib import Path
from typing import Dict, List
from rdflib import URIRef

from rdflib.query import ResultRow

from csvcubed.utils.sparql import none_or_map
from csvcubed.utils.printable import (
    get_printable_list_str,
    get_printable_tabular_list_str,
    get_printable_tabular_str,
)
from csvcubed.utils.qb.components import get_printable_component_property


@dataclass()
class CatalogMetadataModel:
    """
    Model to represent Catalog metadata
    """

    title: str
    label: str
    issued: str
    modified: str
    license: str
    creator: str
    publisher: str
    landing_pages: list[str]
    themes: list[str]
    keywords: list[str]
    contact_point: str
    identifier: str
    comment: str
    description: str

    @property
    def output_str(self) -> str:
        formatted_landing_pages: str = get_printable_list_str(self.landing_pages)
        formatted_themes: str = get_printable_list_str(self.themes)
        formatted_keywords: str = get_printable_list_str(self.keywords)
        formatted_description: str = self.description.replace(linesep, f"{linesep}\t\t")
        return f"{linesep}\t- Title: {self.title}{linesep}\t- Label: {self.label}{linesep}\t- Issued: {self.issued}{linesep}\t- Modified: {self.modified}{linesep}\t- License: {self.license}{linesep}\t- Creator: {self.creator}{linesep}\t- Publisher: {self.publisher}{linesep}\t- Landing Pages: {formatted_landing_pages}{linesep}\t- Themes: {formatted_themes}{linesep}\t- Keywords: {formatted_keywords}{linesep}\t- Contact Point: {self.contact_point}{linesep}\t- Identifier: {self.identifier}{linesep}\t- Comment: {self.comment}{linesep}\t- Description: {formatted_description}"


@dataclass()
class DSDLabelURIModel:
    """
    Model to represent dsd dataset label and uri.
    """

    dataset_label: str
    dsd_uri: URIRef

    @property
    def output_str(self) -> str:
        return f"{linesep}\t- Dataset Label: {self.dataset_label}"


@dataclass()
class QubeComponentModel:
    """
    Model to represent a qube component.
    """

    property: str
    property_label: str
    property_type: str
    csv_col_title: str
    required: bool

    def to_dict(self) -> Dict:
        return {
            "Property": self.property,
            "Property Label": self.property_label,
            "Property Type": self.property_type,
            "Column Title": self.csv_col_title,
            "Required": self.required,
        }


@dataclass()
class QubeComponentsModel:
    """
    Model to represent qube components.
    """

    qube_components: list[QubeComponentModel]
    num_components: int

    @property
    def output_str(self) -> str:
        formatted_components = get_printable_tabular_str(
            [component.to_dict() for component in self.qube_components]
        )
        return f"{linesep}\t- Number of Components: {self.num_components}{linesep}\t- Components:{linesep}{formatted_components}"


@dataclass()
class ColsWithSuppressOutputTrueModel:
    """
    Model to represent cols where the suppress output is true.
    """

    columns: list[str]

    @property
    def output_str(self) -> str:
        return f"{linesep}- Columns where suppress output is true: {get_printable_list_str(self.columns)}"


@dataclass()
class CodelistModel:
    """
    Model to represent a codelist.
    """

    codeList: str
    codeListLabel: str
    colsInUsed: list[str]

    def to_dict(self) -> Dict:
        return {
            "Code List": self.codeList,
            "Code List Label": self.codeListLabel,
            "Columns Used In": get_printable_tabular_list_str(self.colsInUsed),
        }


@dataclass()
class CodelistsModel:
    """
    Model to represent codelists.
    """

    codelists: list[CodelistModel]
    num_codelists: int

    @property
    def output_str(self) -> str:
        formatted_codelists = get_printable_tabular_str(
            [codelist.to_dict() for codelist in self.codelists]
        )
        return f"{linesep}\t- Number of Code Lists: {self.num_codelists}{linesep}\t- Code Lists:{linesep}{formatted_codelists}"


def map_catalog_metadata_result(sparql_result: ResultRow) -> CatalogMetadataModel:
    """
    Maps sparql query to `CatalogMetadataModel`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `CatalogMetadataModel`
    """
    result_dict = sparql_result.asdict()

    model = CatalogMetadataModel(
        title=str(result_dict["title"]),
        label=str(result_dict["label"]),
        issued=str(result_dict["issued"]),
        modified=str(result_dict["modified"]),
        license=none_or_map(result_dict.get("license"), str) or "None",
        creator=none_or_map(result_dict.get("creator"), str) or "None",
        publisher=none_or_map(result_dict.get("publisher"), str) or "None",
        landing_pages=str(result_dict["landingPages"]).split("|"),
        themes=str(result_dict["themes"]).split("|"),
        keywords=str(result_dict["keywords"]).split("|"),
        contact_point=none_or_map(result_dict.get("contactPoint"), str) or "None",
        identifier=str(result_dict["identifier"]) or "None",
        comment=none_or_map(result_dict.get("comment"), str) or "None",
        description=none_or_map(result_dict.get("description"), str) or "None",
    )
    return model


def map_dataset_label_dsd_uri_sparql_result(
    sparql_result: ResultRow,
) -> DSDLabelURIModel:
    """
    Maps sparql query to `DSDLabelURIModel`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `DSDLabelURIModel`
    """
    result_dict = sparql_result.asdict()

    model = DSDLabelURIModel()
    model.dataset_label = str(result_dict["dataSetLabel"])
    model.dsd_uri = URIRef(result_dict["dataStructureDefinition"])

    return model


def map_qube_component_sparql_result(
    sparql_result: ResultRow, json_path: Path
) -> QubeComponentModel:
    """
    Maps sparql query to `QubeComponentModel`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `QubeComponentModel`
    """
    result_dict = sparql_result.asdict()

    model = QubeComponentModel()
    model.property = get_printable_component_property(
        json_path, str(result_dict["componentProperty"])
    )
    model.property_label = (
        none_or_map(result_dict.get("componentPropertyLabel"), str) or ""
    )
    model.property_type = (
        none_or_map(result_dict.get("componentPropertyType"), str) or ""
    )
    model.csv_col_title = none_or_map(result_dict.get("csvColumnTitle"), str) or ""
    model.required = none_or_map(result_dict.get("required"), bool)

    return model


def map_qube_components_sparql_result(
    sparql_results: List[ResultRow], json_path: Path
) -> QubeComponentsModel:
    """
    Maps sparql query to `QubeComponentsModel`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `QubeComponentsModel`
    """
    model = QubeComponentsModel()
    model.qube_components = list(
        map(
            lambda result: map_qube_component_sparql_result(result, json_path),
            sparql_results,
        )
    )
    model.num_components = len(model.qube_components)
    return model


def map_cols_with_supress_output_true_sparql_result(
    sparql_results: List[ResultRow],
) -> ColsWithSuppressOutputTrueModel:
    """
    Maps sparql query to `ColsWithSuppressOutputTrueModel`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `ColsWithSuppressOutputTrueModel`
    """
    model = ColsWithSuppressOutputTrueModel()
    model.columns = list(
        map(
            lambda result: str(result["csvColumnTitle"]),
            sparql_results,
        )
    )


def map_codelist_sparql_result(
    sparql_result: ResultRow, json_path: Path
) -> CodelistModel:
    """
    Maps sparql query to `CodelistModel`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `CodelistModel`
    """
    result_dict = sparql_result.asdict()

    model = CodelistModel()
    model.codeList = (
        get_printable_component_property(json_path, str(result_dict["codeList"])),
    )
    model.codeListLabel = none_or_map(result_dict.get("codeListLabel"), str) or ""
    model.colsInUsed = str(result_dict["csvColumnsUsedIn"]).split("|")

    return model


def map_codelists_sparql_result(
    sparql_results: List[ResultRow], json_path: Path
) -> QubeComponentsModel:
    """
    Maps sparql query to `QubeComponentsModel`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `QubeComponentsModel`
    """
    model = CodelistsModel()
    model.codelists = list(
        map(
            lambda result: map_codelist_sparql_result(result, json_path),
            sparql_results,
        )
    )
    model.num_codelists = len(model.codelists)
    return model
