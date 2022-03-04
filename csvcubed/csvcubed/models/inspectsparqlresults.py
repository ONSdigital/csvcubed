"""
Inspect SPARQL query results
----------------------------
"""

from os import linesep
from pathlib import Path
from typing import List
from dataclasses import dataclass

from rdflib import URIRef
from rdflib.query import ResultRow

from csvcubedmodels.dataclassbase import DataClassBase
from csvcubed.utils.sparql import none_or_map
from csvcubed.utils.printable import (
    get_printable_list_str,
    get_printable_tabular_list_str,
    get_printable_tabular_str,
)
from csvcubed.utils.qb.components import (
    get_printable_component_property,
    get_printable_component_property_type,
)


@dataclass()
class CatalogMetadataResult:
    """
    Model to represent select catalog metadata sparql query result.
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
class DSDLabelURIResult:
    """
    Model to represent select dsd dataset label and uri sparql query result.
    """

    dataset_label: str
    dsd_uri: URIRef

    @property
    def output_str(self) -> str:
        return f"{linesep}\t- Dataset Label: {self.dataset_label}"


@dataclass()
class QubeComponentResult(DataClassBase):
    """
    Model to represent a qube component.
    """

    property: str
    property_label: str
    property_type: str
    csv_col_title: str
    required: bool


@dataclass()
class QubeComponentsResult:
    """
    Model to represent select qube components sparql query result.
    """

    qube_components: list[QubeComponentResult]
    num_components: int

    @property
    def output_str(self) -> str:
        formatted_components = get_printable_tabular_str(
            [component.as_dict() for component in self.qube_components],
            column_names=[
                "Property",
                "Property Label",
                "Property Type",
                "Column Title",
                "Required",
            ],
        )
        return f"{linesep}\t- Number of Components: {self.num_components}{linesep}\t- Components:{linesep}{formatted_components}"


@dataclass()
class ColsWithSuppressOutputTrueResult:
    """
    Model to represent select cols where the suppress output is true sparql query result.
    """

    columns: list[str]

    @property
    def output_str(self) -> str:
        return f"{linesep}- Columns where suppress output is true: {get_printable_list_str(self.columns)}"


@dataclass()
class CodelistResult(DataClassBase):
    """
    Model to represent a codelist.
    """

    codeList: str
    codeListLabel: str
    colsInUsed: str


@dataclass()
class CodelistsResult:
    """
    Model to represent select codelists sparql query result.
    """

    codelists: list[CodelistResult]
    num_codelists: int

    @property
    def output_str(self) -> str:
        formatted_codelists = get_printable_tabular_str(
            [codelist.as_dict() for codelist in self.codelists],
            column_names=["Code List", "Code List Label", "Columns Used In"],
        )
        return f"{linesep}\t- Number of Code Lists: {self.num_codelists}{linesep}\t- Code Lists:{linesep}{formatted_codelists}"


def map_catalog_metadata_result(sparql_result: ResultRow) -> CatalogMetadataResult:
    """
    Maps sparql query to `CatalogMetadataResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `CatalogMetadataResult`
    """
    result_dict = sparql_result.asdict()

    result = CatalogMetadataResult(
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
    return result


def map_dataset_label_dsd_uri_sparql_result(
    sparql_result: ResultRow,
) -> DSDLabelURIResult:
    """
    Maps sparql query to `DSDLabelURIResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `DSDLabelURIResult`
    """
    result_dict = sparql_result.asdict()

    result = DSDLabelURIResult(
        dataset_label=str(result_dict["dataSetLabel"]),
        dsd_uri=URIRef(str(result_dict["dataStructureDefinition"])),
    )
    return result


def map_qube_component_sparql_result(
    sparql_result: ResultRow, json_path: Path
) -> QubeComponentResult:
    """
    Maps sparql query to `QubeComponentResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `QubeComponentResult`
    """
    result_dict = sparql_result.asdict()

    result = QubeComponentResult(
        property=get_printable_component_property(
            json_path, str(result_dict["componentProperty"])
        ),
        property_label=(
            none_or_map(result_dict.get("componentPropertyLabel"), str) or ""
        ),
        property_type=get_printable_component_property_type(
            str(result_dict["componentPropertyType"])
        ),
        csv_col_title=none_or_map(result_dict.get("csvColumnTitle"), str) or "",
        required=none_or_map(result_dict.get("required"), bool) or False,
    )
    return result


def map_qube_components_sparql_result(
    sparql_results: List[ResultRow], json_path: Path
) -> QubeComponentsResult:
    """
    Maps sparql query to `QubeComponentsResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `QubeComponentsResult`
    """
    components = list(
        map(
            lambda result: map_qube_component_sparql_result(result, json_path),
            sparql_results,
        )
    )
    result = QubeComponentsResult(
        qube_components=components, num_components=len(components)
    )
    return result


def map_cols_with_supress_output_true_sparql_result(
    sparql_results: List[ResultRow],
) -> ColsWithSuppressOutputTrueResult:
    """
    Maps sparql query to `ColsWithSuppressOutputTrueResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `ColsWithSuppressOutputTrueResult`
    """
    columns = list(
        map(
            lambda result: str(result["csvColumnTitle"]),
            sparql_results,
        )
    )
    result = ColsWithSuppressOutputTrueResult(columns=columns)
    return result


def map_codelist_sparql_result(
    sparql_result: ResultRow, json_path: Path
) -> CodelistResult:
    """
    Maps sparql query to `CodelistResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `CodelistResult`
    """
    result_dict = sparql_result.asdict()

    result = CodelistResult(
        codeList=get_printable_component_property(
            json_path, str(result_dict["codeList"])
        ),
        codeListLabel=none_or_map(result_dict.get("codeListLabel"), str) or "",
        colsInUsed=get_printable_tabular_list_str(
            str(result_dict["csvColumnsUsedIn"]).split("|")
        ),
    )
    return result


def map_codelists_sparql_result(
    sparql_results: List[ResultRow], json_path: Path
) -> CodelistsResult:
    """
    Maps sparql query to `CodelistsModel`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `CodelistsModel`
    """
    codelists = list(
        map(
            lambda result: map_codelist_sparql_result(result, json_path),
            sparql_results,
        )
    )
    result = CodelistsResult(codelists=codelists, num_codelists=len(codelists))
    return result
