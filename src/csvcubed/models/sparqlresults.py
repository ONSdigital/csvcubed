"""
SPARQL query results
----------------------------
"""

import logging
from dataclasses import dataclass
from os import linesep
from pathlib import Path
from typing import List, Optional, Dict, Any

from csvcubedmodels.dataclassbase import DataClassBase
from rdflib.query import ResultRow

from csvcubed.utils.printable import (
    get_printable_list_str,
    get_printable_tabular_list_str,
    get_printable_tabular_str_from_list,
)
from csvcubed.utils.qb.components import (
    get_component_property_as_relative_path,
    get_component_property_type,
)
from csvcubed.utils.sparql_handler.sparql import none_or_map

_logger = logging.getLogger(__name__)


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
    observation_value_column_titles: Optional[str]
    required: bool


@dataclass
class ObsValDsdComponentResult(DataClassBase):
    """
    Model to represent a observation value result.
    """

    csv_column_property_url: Optional[str]
    observation_value_column_titles: Optional[str]


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
                "Observation Value Column Titles",
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

    code_list: str
    code_list_label: str
    cols_used_in: str


@dataclass
class CSVWTableSchemaFileDependenciesResult:
    """
    Model to represent select csvw table schema file dependencies result.
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
            [
                codelist.as_dict()
                for codelist in sorted(self.codelists, key=lambda c: c.code_list)
            ],
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

    column_property_url: Optional[str]
    column_value_url: Optional[str]
    column_title: Optional[str]
    column_name: Optional[str]


@dataclass
class CodeListColsByDatasetUrlResult:
    """
    Model to represent select codelist columns by table url.
    """

    columns: List[CodelistColumnResult]


@dataclass
class PrimaryKeyColNameByDatasetUrlResult:
    """
    Model to represent select primary key column name by table url.
    """

    value: str


@dataclass
class PrimaryKeyColNamesByDatasetUrlResult:
    """
    Model to represent select primary keys by table url.
    """

    primary_key_col_names: List[PrimaryKeyColNameByDatasetUrlResult]


@dataclass
class MetadataDependenciesResult:
    """
    Model representing a metadata dependency which should be loaded to make sense of the current graph.
    """

    data_set: str
    data_dump: str
    uri_space: str


@dataclass
class TableSchemaPropertiesResult:
    """
    Model representing the table schema value url and about url.
    """

    about_url: str
    value_url: str
    table_url: str


@dataclass
class IsPivotedShapeMeasureResult:
    """
    A dataclass that is used to return the measure of from a cube's metadata and whether that measure is part of a pivoted or standard shape cube.
    """

    measure: str
    is_pivoted_shape: bool

@dataclass
class UnitColumnAboutValueUrlResult:
    """
    Model representing the About URL and Value URL of the unit column
    """
    csv_url: str
    about_url: Optional[str]
    value_url: str

@dataclass
class ObservationValueColumnTitleAboutUrlResult:
    """
    Model representing the Column Title and About URL of an observation value
    """
    csv_url: str
    observation_value_col_title: str
    observation_value_col_about_url: Optional[str]

@dataclass
class ColTitlesAndNamesResult:
    """
    Model representing the Column Titles and Column Names of a data set.
    """
    csv_url: str
    column_name: str
    column_title: Optional[str]

def map_catalog_metadata_result(sparql_result: ResultRow) -> CatalogMetadataResult:
    """
    Maps sparql query result to `CatalogMetadataResult`

    Member of :file:`./models/sparqlresults.py`

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

    Member of :file:`./models/sparqlresults.py`

    :return: `DSDLabelURIResult`
    """
    result_dict = sparql_result.asdict()

    result = DSDLabelURIResult(
        dataset_label=str(result_dict["dataSetLabel"]),
        dsd_uri=str(result_dict["dataStructureDefinition"]),
    )
    return result


def _map_qube_component_sparql_result(
    sparql_result: ResultRow, json_path: Path
) -> QubeComponentResult:
    """
    Maps sparql query result to `QubeComponentResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `QubeComponentResult`
    """
    result_dict = sparql_result.asdict()
    _logger.debug("result_dict: %s", result_dict)

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
        observation_value_column_titles="",  # This value is popuated after runnning the SELECT_OBS_VAL_FOR_DSD_COMPONENT_PROPERTIES sparql query. The _map_obs_val_for_dsd_component_properties_results will set the value for this property.
        required=none_or_map(result_dict.get("required"), bool) or False,
    )
    return result


def _map_obs_val_for_dsd_component_properties_results(
    sparql_results: List[ResultRow],
) -> List[ObsValDsdComponentResult]:
    def map_row(row_result: Dict[str, Any]) -> ObsValDsdComponentResult:
        return ObsValDsdComponentResult(
            csv_column_property_url=none_or_map(
                row_result.get("csvColumnPropertyUrl"), str
            ),
            observation_value_column_titles=none_or_map(
                row_result.get("observationValueColumnTitles"), str
            ),
        )

    return [map_row(row.asdict()) for row in sparql_results]


def map_qube_components_sparql_result(
    sparql_results_dsd_components: List[ResultRow],
    sparql_results_obs_val_col_titles: Optional[List[ResultRow]],
    json_path: Path,
) -> QubeComponentsResult:
    """
    Maps sparql query result to `QubeComponentsResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `QubeComponentsResult`
    """
    obs_val_col_title_results: Optional[List[ObsValDsdComponentResult]] = None
    if sparql_results_obs_val_col_titles is not None:
        obs_val_col_title_results = _map_obs_val_for_dsd_component_properties_results(
            sparql_results_obs_val_col_titles
        )

    components: List[QubeComponentResult] = []
    for result in sparql_results_dsd_components:
        dsd_component_result: QubeComponentResult = _map_qube_component_sparql_result(
            result, json_path
        )
        if obs_val_col_title_results is not None:
            obs_val_col_title_result_for_component = [
                obs_val_col_title_result
                for obs_val_col_title_result in obs_val_col_title_results
                if obs_val_col_title_result.csv_column_property_url
                == dsd_component_result.property
            ]

            if len(obs_val_col_title_result_for_component) == 1:
                dsd_component_result.observation_value_column_titles = (
                    obs_val_col_title_result_for_component[
                        0
                    ].observation_value_column_titles
                )

        components.append(dsd_component_result)

    result = QubeComponentsResult(
        qube_components=components, num_components=len(components)
    )
    return result


def map_cols_with_supress_output_true_sparql_result(
    sparql_results: List[ResultRow],
) -> ColsWithSuppressOutputTrueResult:
    """
    Maps sparql query result to `ColsWithSuppressOutputTrueResult`

    Member of :file:`./models/sparqlresults.py`

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


def _map_codelist_sparql_result(
    sparql_result: ResultRow, json_path: Path
) -> CodelistResult:
    """
    Maps sparql query result to `CodelistResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `CodelistResult`
    """
    result_dict = sparql_result.asdict()

    result = CodelistResult(
        code_list=get_component_property_as_relative_path(
            json_path, str(result_dict["codeList"])
        ),
        code_list_label=none_or_map(result_dict.get("codeListLabel"), str) or "",
        cols_used_in=get_printable_tabular_list_str(
            str(result_dict["csvColumnsUsedIn"]).split("|")
        ),
    )
    return result


def map_codelists_sparql_result(
    sparql_results: List[ResultRow], json_path: Path
) -> CodelistsResult:
    """
    Maps sparql query result to `CodelistsModel`

    Member of :file:`./models/sparqlresults.py`

    :return: `CodelistsModel`
    """
    codelists = list(
        map(
            lambda result: _map_codelist_sparql_result(result, json_path),
            sparql_results,
        )
    )
    result = CodelistsResult(codelists=codelists, num_codelists=len(codelists))
    return result


def map_csvw_table_schemas_file_dependencies_result(
    sparql_results: List[ResultRow],
) -> CSVWTableSchemaFileDependenciesResult:
    """
    Maps sparql query result to `CSVWTableSchemaFileDependenciesResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `CSVWTableSchemaFileDependenciesResult`
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

    Member of :file:`./models/sparqlresults.py`

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

    Member of :file:`./models/sparqlresults.py`

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


def _map_codelist_column_sparql_result(
    sparql_result: ResultRow,
) -> CodelistColumnResult:
    """
    Maps sparql query result to `CodelistColumnResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `CodelistColumnResult`
    """
    result_dict = sparql_result.asdict()

    result = CodelistColumnResult(
        column_property_url=none_or_map(result_dict.get("columnPropertyUrl"), str),
        column_value_url=none_or_map(result_dict.get("columnValueUrl"), str),
        column_title=none_or_map(result_dict.get("columnTitle"), str),
        column_name=none_or_map(result_dict.get("columnName"), str),
    )
    return result


def map_codelist_cols_by_dataset_url_result(
    sparql_results: List[ResultRow],
) -> CodeListColsByDatasetUrlResult:
    """
    Maps sparql query result to `CodeListColsByDatasetUrlResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `CodeListColsByDatasetUrlResult`
    """

    columns = list(
        map(
            lambda result: _map_codelist_column_sparql_result(result),
            sparql_results,
        )
    )
    result = CodeListColsByDatasetUrlResult(columns=columns)
    return result


def _map_primary_key_col_name_by_dataset_url_result(
    sparql_result: ResultRow,
) -> PrimaryKeyColNameByDatasetUrlResult:
    """
    Maps sparql query result to `PrimaryKeyColNameByDatasetUrlResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `PrimaryKeyColNameByDatasetUrlResult`
    """
    result_dict = sparql_result.asdict()

    result = PrimaryKeyColNameByDatasetUrlResult(
        value=str(result_dict["tablePrimaryKey"]),
    )
    return result


def map_primary_key_col_names_by_dataset_url_result(
    sparql_results: List[ResultRow],
) -> PrimaryKeyColNamesByDatasetUrlResult:
    """
    Maps sparql query result to `PrimaryKeyColNamesByDatasetUrlResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `PrimaryKeyColNamesByDatasetUrlResult`
    """
    primary_key_col_names = list(
        map(
            lambda result: _map_primary_key_col_name_by_dataset_url_result(result),
            sparql_results,
        )
    )
    result = PrimaryKeyColNamesByDatasetUrlResult(
        primary_key_col_names=primary_key_col_names
    )
    return result


def map_metadata_dependency_results(
    sparql_results: List[ResultRow],
) -> List[MetadataDependenciesResult]:
    def map_row(row_result: Dict[str, Any]) -> MetadataDependenciesResult:
        return MetadataDependenciesResult(
            data_set=str(row_result["dataset"]),
            data_dump=str(row_result["dataDump"]),
            uri_space=str(row_result["uriSpace"]),
        )

    return [map_row(row.asdict()) for row in sparql_results]


def map_table_schema_properties_result(
    sparql_result: ResultRow,
) -> TableSchemaPropertiesResult:
    """
    Maps sparql query result to `TableSchemaPropertiesResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `TableSchemaPropertiesResult`
    """
    result_dict = sparql_result.asdict()

    result = TableSchemaPropertiesResult(
        about_url=str(result_dict["tableAboutUrl"]),
        value_url=str(result_dict["columnValueUrl"]),
        table_url=str(result_dict["csvUrl"]),
    )
    return result


def map_is_pivoted_shape_for_measures_in_data_set(
    sparql_results: List[ResultRow],
) -> List[IsPivotedShapeMeasureResult]:
    """
    Maps the sparql query result to objects of type IsPivotedMeasureResult that are then returned.
    """

    def map_row(row_result: Dict[str, Any]) -> IsPivotedShapeMeasureResult:
        return IsPivotedShapeMeasureResult(
            measure=str(row_result["measure"]),
            is_pivoted_shape=bool(row_result["isPivotedShape"]),
        )

    return [map_row(row.asdict()) for row in sparql_results]

def map_unit_col_about_value_urls_result(
    sparql_results: List[ResultRow]
) -> List[UnitColumnAboutValueUrlResult]:
    """
    Maps SPARQL query results to 'UnitColumnAboutValueUrlResult'
    """
    def map_row(row_result: Dict[str, Any]) -> UnitColumnAboutValueUrlResult:
        return UnitColumnAboutValueUrlResult(
            csv_url=str(row_result["csvUrl"]),
            about_url=none_or_map(row_result.get("aboutUrl"), str),
            value_url=str(row_result["valueUrl"])
        )
    return [map_row(row.asdict()) for row in sparql_results]


def map_observation_value_col_title_and_about_url_result(
    sparql_results: List[ResultRow]
) -> List[ObservationValueColumnTitleAboutUrlResult]:
    """
    Maps SPARQL query results to 'ObservationValueColumnTitleAboutUrlResult'
    """
    def map_row(row_result: Dict[str, Any]) -> ObservationValueColumnTitleAboutUrlResult:
        return ObservationValueColumnTitleAboutUrlResult(
            csv_url=str(row_result["csvUrl"]),
            observation_value_col_title=str(row_result["observationValueColumnTitle"]),
            observation_value_col_about_url=none_or_map(row_result.get("observationValueColumnAboutUrl"), str)
        )
    return [map_row(row.asdict()) for row in sparql_results]

def map_col_tiles_and_names_result(sparql_results: List[ResultRow]) -> List[ColTitlesAndNamesResult]:
    """
    Maps SPARQL query results to 'ColTitlesAndNamesResult'
    """
    def map_row(row_result: Dict[str, Any]) -> ColTitlesAndNamesResult:
        return ColTitlesAndNamesResult(
            csv_url=str(row_result["csvUrl"]),
            column_name=str(row_result["columnName"]),
            column_title=none_or_map(row_result.get("columnTitle"), str)
        )
    return [map_row(row.asdict()) for row in sparql_results]