"""
Inspect SPARQL query results
----------------------------
"""

from dataclasses import dataclass
from os import linesep
from pathlib import Path
from typing import Dict, List
from csvcubedmodels.dataclassbase import DataClassBase
from rdflib import URIRef

from rdflib.query import ResultRow

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
class QubeComponentModel(DataClassBase):
    """
    Model to represent a qube component.
    """

    property: str
    property_label: str
    property_type: str
    csv_col_title: str
    required: bool


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
class ColsWithSuppressOutputTrueModel:
    """
    Model to represent cols where the suppress output is true.
    """

    columns: list[str]

    @property
    def output_str(self) -> str:
        return f"{linesep}- Columns where suppress output is true: {get_printable_list_str(self.columns)}"


@dataclass()
class CodelistModel(DataClassBase):
    """
    Model to represent a codelist.
    """

    codeList: str
    codeListLabel: str
    colsInUsed: str


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
            [codelist.as_dict() for codelist in self.codelists],
            column_names=["Code List", "Code List Label", "Columns Used In"],
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

    model = DSDLabelURIModel(
        dataset_label=str(result_dict["dataSetLabel"]),
        dsd_uri=URIRef(result_dict["dataStructureDefinition"]),
    )
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

    model = QubeComponentModel(
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
    return model


def map_qube_components_sparql_result(
    sparql_results: List[ResultRow], json_path: Path
) -> QubeComponentsModel:
    """
    Maps sparql query to `QubeComponentsModel`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `QubeComponentsModel`
    """
    components = list(
        map(
            lambda result: map_qube_component_sparql_result(result, json_path),
            sparql_results,
        )
    )
    model = QubeComponentsModel(
        qube_components=components, num_components=len(components)
    )
    return model


def map_cols_with_supress_output_true_sparql_result(
    sparql_results: List[ResultRow],
) -> ColsWithSuppressOutputTrueModel:
    """
    Maps sparql query to `ColsWithSuppressOutputTrueModel`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `ColsWithSuppressOutputTrueModel`
    """
    columns = list(
        map(
            lambda result: str(result["csvColumnTitle"]),
            sparql_results,
        )
    )
    model = ColsWithSuppressOutputTrueModel(columns=columns)
    return model


def map_codelist_sparql_result(
    sparql_result: ResultRow, json_path: Path
) -> CodelistModel:
    """
    Maps sparql query to `CodelistModel`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `CodelistModel`
    """
    result_dict = sparql_result.asdict()

    model = CodelistModel(
        codeList=get_printable_component_property(
            json_path, str(result_dict["codeList"])
        ),
        codeListLabel=none_or_map(result_dict.get("codeListLabel"), str) or "",
        colsInUsed=get_printable_tabular_list_str(
            str(result_dict["csvColumnsUsedIn"]).split("|")
        ),
    )
    return model


def map_codelists_sparql_result(
    sparql_results: List[ResultRow], json_path: Path
) -> CodelistsModel:
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
    model = CodelistsModel(codelists=codelists, num_codelists=len(codelists))
    return model
