"""
Inspect SPARQL query results
----------------------------
"""

import json
from os import linesep
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from rdflib.query import ResultRow

from csvcubedmodels.dataclassbase import DataClassBase
from csvcubed.utils.sparql import none_or_map
from csvcubed.utils.printable import (
    get_printable_list_str,
    get_printable_tabular_list_str,
    get_printable_tabular_str_from_list,
)
from csvcubed.utils.qb.components import (
    get_component_property_as_relative_path,
    get_component_property_type,
)


@dataclass
class CatalogMetadataResult:
    """
    Model to represent select catalog metadata sparql query result.
    """

    dataset_uri: str
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
        return f"""
        - Title: {self.title}
        - Label: {self.label}
        - Issued: {self.issued}
        - Modified: {self.modified}
        - License: {self.license}
        - Creator: {self.creator}
        - Publisher: {self.publisher}
        - Landing Pages: {formatted_landing_pages}
        - Themes: {formatted_themes}
        - Keywords: {formatted_keywords}
        - Contact Point: {self.contact_point}
        - Identifier: {self.identifier}
        - Comment: {self.comment}
        - Description: {formatted_description}
        """


@dataclass
class DSDLabelURIResult:
    """
    Model to represent select dsd dataset label and uri sparql query result.
    """

    dataset_label: str
    dsd_uri: str

    @property
    def output_str(self) -> str:
        return f"""
        - Dataset Label: {self.dataset_label}"""


@dataclass
class QubeComponentResult(DataClassBase):
    """
    Model to represent a qube component.
    """

    property: str
    property_label: Optional[str]
    property_type: str
    csv_col_title: Optional[str]
    required: bool


@dataclass
class QubeComponentsResult:
    """
    Model to represent select qube components sparql query result.
    """

    qube_components: list[QubeComponentResult]
    num_components: int

    @property
    def output_str(self) -> str:
        formatted_components = get_printable_tabular_str_from_list(
            [component.as_dict() for component in self.qube_components],
            column_names=[
                "Property",
                "Property Label",
                "Property Type",
                "Column Title",
                "Required",
            ],
        )
        return f"""
        - Number of Components: {self.num_components}
        - Components:{linesep}{formatted_components}"""


@dataclass
class ColsWithSuppressOutputTrueResult:
    """
    Model to represent select cols where the suppress output is true sparql query result.
    """

    columns: list[str]

    @property
    def output_str(self) -> str:
        return f"""
        - Columns where suppress output is true: {get_printable_list_str(self.columns)}"""


@dataclass
class CodelistResult(DataClassBase):
    """
    Model to represent a codelist.
    """

    codeList: str
    codeListLabel: str
    colsInUsed: str


@dataclass
class CSVWTableSchemaFileDependenciesResult:
    """
    Model to represent select csvw table schemas result.
    """

    table_schema_file_dependencies: List[str]


@dataclass
class CodelistsResult:
    """
    Model to represent select codelists sparql query result.
    """

    codelists: list[CodelistResult]
    num_codelists: int

    @property
    def output_str(self) -> str:
        formatted_codelists = get_printable_tabular_str_from_list(
            [codelist.as_dict() for codelist in self.codelists],
            column_names=["Code List", "Code List Label", "Columns Used In"],
        )
        return f"""
        - Number of Code Lists: {self.num_codelists}
        - Code Lists:{linesep}{formatted_codelists}"""


@dataclass
class DatasetURLResult:
    """
    Model to represent select dataset url result.
    """

    dataset_url: str


@dataclass
class DSDSingleUnitResult:
    """
    Model to represent select single unit from dsd.
    """

    unit_uri: str
    unit_label: Optional[str]


@dataclass
class CodelistColumnResult(DataClassBase):
    """
    Model to represent a codelist column.
    """

    column_property_url: str
    column_value_url: Optional[str]
    column_title: Optional[str]

@dataclass
class CodeListColsByDatasetUrlResult:
    """
    Model to represent select codelist columns by table url.
    """

    columns: List[CodelistColumnResult]


def map_catalog_metadata_result(sparql_result: ResultRow) -> CatalogMetadataResult:
    """
    Maps sparql query result to `CatalogMetadataResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `CatalogMetadataResult`
    """
    result_dict = sparql_result.asdict()

    result = CatalogMetadataResult(
        dataset_uri=str(result_dict["dataset"]),
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
        identifier=none_or_map(result_dict.get("identifier"), str) or "None",
        comment=none_or_map(result_dict.get("comment"), str) or "None",
        description=none_or_map(result_dict.get("description"), str) or "None",
    )
    return result


def map_dataset_label_dsd_uri_sparql_result(
    sparql_result: ResultRow,
) -> DSDLabelURIResult:
    """
    Maps sparql query result to `DSDLabelURIResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `DSDLabelURIResult`
    """
    result_dict = sparql_result.asdict()

    result = DSDLabelURIResult(
        dataset_label=str(result_dict["dataSetLabel"]),
        dsd_uri=str(result_dict["dataStructureDefinition"]),
    )
    return result


def map_qube_component_sparql_result(
    sparql_result: ResultRow, json_path: Path
) -> QubeComponentResult:
    """
    Maps sparql query result to `QubeComponentResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `QubeComponentResult`
    """
    result_dict = sparql_result.asdict()

    result = QubeComponentResult(
        property=get_component_property_as_relative_path(
            json_path, str(result_dict["componentProperty"])
        ),
        property_label=(
            none_or_map(result_dict.get("componentPropertyLabel"), str) or ""
        ),
        property_type=get_component_property_type(
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
    Maps sparql query result to `QubeComponentsResult`

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
    Maps sparql query result to `ColsWithSuppressOutputTrueResult`

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
    Maps sparql query result to `CodelistResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `CodelistResult`
    """
    result_dict = sparql_result.asdict()

    result = CodelistResult(
        codeList=get_component_property_as_relative_path(
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
    Maps sparql query result to `CodelistsModel`

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


def map_csvw_table_schemas_result(
    sparql_results: List[ResultRow],
) -> CSVWTableSchemaFileDependenciesResult:
    """
    Maps sparql query result to `CSVWTabelSchemasResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `CSVWTabelSchemasResult`
    """

    result = CSVWTableSchemaFileDependenciesResult(
        table_schema_file_dependencies=[
            str(sparql_result["tableSchema"]) for sparql_result in sparql_results
        ]
    )
    return result


def map_dataset_url_result(
    sparql_result: ResultRow,
) -> DatasetURLResult:
    """
    Maps sparql query result to `DatasetURLResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `DatasetURLResult`
    """
    result_dict = sparql_result.asdict()

    result = DatasetURLResult(dataset_url=str(result_dict["tableUrl"]))
    return result


def map_single_unit_from_dsd_result(
    sparql_result: ResultRow, json_path: Path
) -> DSDSingleUnitResult:
    """
    Maps sparql query result to `DSDSingleUnitResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `DSDSingleUnitResult`
    """
    result_dict = sparql_result.asdict()
    unit_label = none_or_map(result_dict.get("unitLabel"), str)

    result = DSDSingleUnitResult(
        unit_uri=get_component_property_as_relative_path(
            json_path, str(result_dict["unitUri"])
        ),
        unit_label=unit_label,
    )
    return result


def map_codelist_column_sparql_result(sparql_result: ResultRow) -> CodelistColumnResult:
    """
    Maps sparql query result to `CodelistColumnResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `CodelistColumnResult`
    """
    result_dict = sparql_result.asdict()

    result = CodelistColumnResult(
        column_property_url=str(result_dict["columnPropertyUrl"]),
        column_value_url=none_or_map(result_dict.get("columnValueUrl"), str),
        column_title=none_or_map(result_dict.get("columnTitle"), str),
    )
    return result


def map_codelist_cols_by_dataset_url_result(
    sparql_results: List[ResultRow],
) -> CodeListColsByDatasetUrlResult:
    """
    Maps sparql query result to `CodeListColsByDatasetUrlResult`

    Member of :file:`./models/inspectsparqlresults.py`

    :return: `CodeListColsByDatasetUrlResult`
    """

    columns = list(
        map(
            lambda result: map_codelist_column_sparql_result(result),
            sparql_results,
        )
    )
    result = CodeListColsByDatasetUrlResult(columns=columns)
    return result
